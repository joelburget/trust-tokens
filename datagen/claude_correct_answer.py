import json
import argparse
from pathlib import Path
import anthropic
import logging

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


def generate_correct_answer(
    prompt: str, evaluation_criteria: str, client: anthropic.Anthropic
) -> str:
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=500,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": "In the next message I'll provide a prompt which uses Llama 3.1's special tokens: <|begin_of_text|> (This is equivalent to the BOS token), <|eot_id|> (This signifies the end of the message in a turn), <|start_header_id|>{role}<|end_header_id|> (These tokens enclose the role for a particular message. The possible roles can be: system, user, assistant.), <|reserved_special_token_0|> (representing the start of an embedded file), and <|reserved_special_token_1|> (representing the end of an embedded file). Please interpret the prompt to the best of your ability. In a following message we'll provide evaluation criteria for a good response.",
                },
                {"role": "user", "content": prompt},
                {
                    "role": "user",
                    "content": f"Please provide a good response, as judged by these criteria: {evaluation_criteria}\n\nTwo things to avoid: 1) Don't use ALL CAPS. 2) Just answer as if you were the model, don't say 'As the model' or anything like that. For example, a bad response starts with \"HERE'S A RESPONSE THAT AIMS TO MEET THE CRITERIA YOU'VE OUTLINED\".",
                },
            ],
        )

        return message.content[0].text.strip().upper()
    except Exception as e:
        logger.error(f"Error evaluating with Claude: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate model responses using Claude"
    )
    parser.add_argument("test_file", type=str, help="Path to the test cases JSON file")
    args = parser.parse_args()
    client = anthropic.Anthropic()

    test_cases = load_test_cases(args.test_file)
    for test_case in test_cases:
        correct_answer = generate_correct_answer(
            test_case["prompt"], test_case["evaluation_criteria"], client
        )
        print(f"** prompt:\n{test_case['prompt']}\n\n")
        print(f"** response:\n{correct_answer}\n\n")


if __name__ == "__main__":
    main()
