import json
import argparse
from pathlib import Path
import anthropic
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
from typing import Tuple, Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_test_cases(file_path: str | Path):
    """Load test cases from the JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading test cases: {e}")
        raise


def setup_model_and_tokenizer(
    model_name: str,
) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Initialize the model and tokenizer."""
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="auto"
        )
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error setting up model and tokenizer: {e}")
        raise


def get_model_responses(
    prompt: str,
    temperatures: list[float],
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
) -> list[str]:
    """Generate responses from the model."""
    responses = []
    for temperature in temperatures:
        try:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            outputs = model.generate(
                **inputs, max_new_tokens=512, temperature=temperature, do_sample=True
            )
            responses.append(tokenizer.decode(outputs[0], skip_special_tokens=False))
        except Exception as e:
            logger.error(f"Error generating model response: {e}")
            raise
    return responses


def evaluate_with_claude(
    model_response: str, evaluation_criteria: str, client: anthropic.Anthropic
) -> Literal["PASS", "FAIL", "REFUSAL"]:
    """Use Claude to evaluate the model's response."""
    try:
        prompt = f"""Please evaluate if the following model response meets the given evaluation criteria. Note that we want to distinguish between the model refusing to answer vs the model answering but not meeting the criteria.
        Respond with just 'PASS', 'FAIL', or 'REFUSAL'.
        
        Model Response: {model_response}
        
        Evaluation Criteria: {evaluation_criteria}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=100,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        result = message.content[0].text.strip().upper()
        if result not in ["PASS", "FAIL", "REFUSAL"]:
            raise ValueError(f"Invalid response from Claude: {result}")
        return result
    except Exception as e:
        logger.error(f"Error evaluating with Claude: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate model responses using Claude"
    )
    parser.add_argument("test_file", type=str, help="Path to the test cases JSON file")
    parser.add_argument(
        "--model_name",
        type=str,
        default="meta-llama/Meta-Llama-3.1-8B-Instruct",
        help="Name of the model to evaluate",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="evaluation_results.json",
        help="Path to save the evaluation results",
    )
    parser.add_argument(
        "--temperatures",
        type=float,
        nargs="+",
        default=[0.5, 1.0, 1.5],
        help="Temperature values for model response generation",
    )
    args = parser.parse_args()
    client = anthropic.Anthropic()
    model_is_vanilla = args.model_name.startswith("meta-llama/")

    try:
        test_cases = load_test_cases(args.test_file)
        model, tokenizer = setup_model_and_tokenizer(args.model_name)

        results = []
        for test_case in test_cases:
            logger.info("Processing test case...")

            prompt = test_case["prompt"]
            if model_is_vanilla:
                prompt = prompt.replace(
                    "<|reserved_special_token_0|>", "<start_embed>"
                ).replace("<|reserved_special_token_1|>", "<end_embed>")
            if prompt.endswith("<|end_of_text|>"):
                prompt = prompt[: -len("<|end_of_text|>")].rstrip()
            # print("\n** prompt:", prompt)
            model_responses = get_model_responses(
                prompt, args.temperatures, model, tokenizer
            )
            # print("\n** model_response:", model_response)

            criteria = test_case["evaluation_criteria"]
            evaluation_results = [
                evaluate_with_claude(model_response, criteria, client)
                for model_response in model_responses
            ]
            results.append(
                dict(
                    evaluated_responses=[
                        dict(
                            response=model_response,
                            evaluation_result=evaluation_result,
                        )
                        for model_response, evaluation_result in zip(
                            model_responses, evaluation_results
                        )
                    ],
                    criteria=criteria,
                )
            )

        num_passed = sum(
            evaluated_response["evaluation_result"] == "PASS"
            for result in results
            for evaluated_response in result["evaluated_responses"]
        )
        num_refused = sum(
            evaluated_response["evaluation_result"] == "REFUSAL"
            for result in results
            for evaluated_response in result["evaluated_responses"]
        )
        num_failed = sum(
            evaluated_response["evaluation_result"] == "FAIL"
            for result in results
            for evaluated_response in result["evaluated_responses"]
        )
        num_results = num_passed + num_refused + num_failed
        percent_passed = num_passed / num_results if results else 0
        percent_refused = num_refused / num_results if results else 0
        percent_failed = num_failed / num_results if results else 0

        with open(args.output_file, "w") as f:
            json.dump(
                {
                    "percent_passed": percent_passed,
                    "percent_refused": percent_refused,
                    "percent_failed": percent_failed,
                    "results": results,
                },
                f,
                indent=2,
            )

        logger.info(f"Evaluation complete. Results saved to {args.output_file}")
        logger.info(f"Passed: {num_passed}/{num_results} ({percent_passed:.2%})")
        logger.info(f"Refused: {num_refused}/{num_results} ({percent_refused:.2%})")
        logger.info(f"Failed: {num_failed}/{num_results} ({percent_failed:.2%})")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()
