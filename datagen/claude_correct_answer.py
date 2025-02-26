import argparse
import uuid
import anthropic
import logging
from tqdm import tqdm
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_correct_answer(
    instructions: str, embed: str, client: anthropic.Anthropic
) -> str:
    try:
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=500,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": f"{instructions}\n\n{embed}",
                },
            ],
        )

        return message.content[0].text.strip()
    except Exception as e:
        logger.error(f"Error evaluating with Claude: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate model responses using Claude"
    )
    parser.add_argument("db_path", type=str, help="Path to the SQLite database")
    args = parser.parse_args()
    client = anthropic.Anthropic()

    conn = sqlite3.connect(args.db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_responses (
          id TEXT PRIMARY KEY,
          scenario_id TEXT,
          correct_answer TEXT
        )
    """)

    cursor.execute("SELECT id, original_instructions, original_embed FROM scenarios")
    test_cases = cursor.fetchall()

    for test_case in tqdm(test_cases):
        id = str(uuid.uuid4())
        correct_answer = generate_correct_answer(test_case[1], test_case[2], client)
        # print(f"** prompt:\n{test_case[1]}\n\n{test_case[2]}\n\n")
        # print(f"** response:\n{correct_answer}\n\n")
        cursor.execute(
            """
            INSERT INTO generated_responses (
                id, scenario_id, correct_answer
            ) VALUES (?, ?, ?)
            """,
            (id, test_case[0], correct_answer),
        )
    conn.commit()


if __name__ == "__main__":
    main()
