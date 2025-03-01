import sqlite3
import os
import sys
from pathlib import Path
from typing import Dict, List, TypedDict
from datasets import Dataset
import pandas as pd
import argparse
from prompt_substitute import prompt_substitute

token = os.getenv("HUGGINGFACE_TOKEN")


class Example(TypedDict):
    instruction: str
    input: str
    trusted_output: str
    untrusted_output: str


class DataItem(TypedDict):
    name: str
    examples: List[Example]


def process_db_to_dataset(db_path: Path) -> Dataset:
    """
    Process SQLite database into a Hugging Face dataset

    Args:
        db_path: Path to the SQLite database

    Returns:
        Dataset: Hugging Face dataset object

    Raises:
        FileNotFoundError: If SQLite database doesn't exist
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        scenarios.id as scenario_id,
        evaluated_responses.id as evaluated_response_id,
        generated_responses.id as generated_response_id,
        prompt,
        evaluated_responses.response as rejected_response, 
        generated_responses.correct_answer as chosen_response,
        evaluation_result
    FROM scenarios
    JOIN evaluated_responses ON evaluated_responses.scenario_id = scenarios.id
    JOIN generated_responses ON generated_responses.scenario_id = scenarios.id
    """)
    test_cases = cursor.fetchall()

    flat_data: Dict[str, List[str]] = {
        "scenario_id": [],
        "evaluated_response_id": [],
        "generated_response_id": [],
        "chosen": [],
        "rejected": [],
    }

    # Flatten the nested structure
    for item in test_cases:
        (
            scenario_id,
            evaluated_response_id,
            generated_response_id,
            prompt,
            rejected_response,
            chosen_response,
            evaluation_result,
        ) = item
        if evaluation_result in ["ANSWER_BOTH", "ANSWER_OVERRIDE"]:
            user_message = {
                "role": "user",
                "content": prompt_substitute(prompt),
            }
            chosen = [
                user_message,
                {"role": "assistant", "content": chosen_response},
            ]
            rejected = [
                user_message,
                {"role": "assistant", "content": rejected_response},
            ]
            flat_data["scenario_id"].append(scenario_id)
            flat_data["evaluated_response_id"].append(evaluated_response_id)
            flat_data["generated_response_id"].append(generated_response_id)
            flat_data["chosen"].append(chosen)
            flat_data["rejected"].append(rejected)

    df = pd.DataFrame(flat_data)
    return Dataset.from_pandas(df)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a dataset to HuggingFace")
    parser.add_argument(
        "repo_name", type=str, help="Repository name in format username/dataset-name"
    )
    parser.add_argument(
        "--db-file",
        type=Path,
        default=Path("scenarios.db"),
        help="Path to SQLite database (default: scenarios.db)",
    )
    args = parser.parse_args()

    try:
        # Validate repository name format
        if "/" not in args.repo_name:
            raise ValueError(
                "Repository name must be in format 'username/dataset-name'"
            )

        # Process the SQLite database into a dataset
        dataset = process_db_to_dataset(args.db_file)
        dataset.push_to_hub(args.repo_name, token=token)
        print(f"\nSuccessfully uploaded dataset to {args.repo_name}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
