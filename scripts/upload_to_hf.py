import json
import os
import sys
from pathlib import Path
from typing import Dict, List, TypedDict
from datasets import Dataset
import pandas as pd
import argparse

token = os.getenv("HUGGINGFACE_TOKEN")


class Example(TypedDict):
    instruction: str
    input: str
    trusted_output: str
    untrusted_output: str


class DataItem(TypedDict):
    name: str
    examples: List[Example]


def process_json_to_dataset(json_file_path: Path) -> Dataset:
    """
    Process JSON file into a Hugging Face dataset

    Args:
        json_file_path: Path to the JSON file

    Returns:
        Dataset: Hugging Face dataset object

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON file is invalid
    """
    with open(json_file_path, "r") as f:
        data: List[DataItem] = json.load(f)

    flat_data: Dict[str, List[str]] = {
        "name": [],
        "instruction": [],
        "input": [],
        "trusted_output": [],
        "untrusted_output": [],
    }

    # Flatten the nested structure
    for item in data:
        name = item["name"]
        for example in item["examples"]:
            flat_data["name"].append(name)
            flat_data["instruction"].append(example["instruction"])
            flat_data["input"].append(example["input"])
            flat_data["trusted_output"].append(example["trusted_output"])
            flat_data["untrusted_output"].append(example["untrusted_output"])

    df = pd.DataFrame(flat_data)
    return Dataset.from_pandas(df)


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload a dataset to HuggingFace")
    parser.add_argument(
        "repo_name", type=str, help="Repository name in format username/dataset-name"
    )
    parser.add_argument(
        "--json-file",
        type=Path,
        default=Path("../datagen/training_example.json"),
        help="Path to JSON file (default: ../datagen/training_example.json)",
    )
    args = parser.parse_args()

    try:
        # Validate repository name format
        if "/" not in args.repo_name:
            raise ValueError(
                "Repository name must be in format 'username/dataset-name'"
            )

        # Process the JSON file into a dataset
        dataset = process_json_to_dataset(args.json_file)
        dataset.push_to_hub(args.repo_name, token=token)
        print(f"\nSuccessfully uploaded dataset to {args.repo_name}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
