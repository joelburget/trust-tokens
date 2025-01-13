import json
import random
import argparse
import os
from anthropic import Anthropic

def load_scenarios(filepath):
    """Load scenarios from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_scenarios(scenarios, filepath):
    """Save scenarios to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(scenarios, f, indent=2)

def select_random_examples(scenarios, n):
    """Randomly select n scenarios from the list."""
    return random.sample(scenarios, min(n, len(scenarios)))

def format_examples_for_prompt(examples):
    """Format examples for inclusion in the prompt."""
    formatted = json.dumps(examples, indent=2)
    return f"Here are some example scenarios:\n\n{formatted}\n\n"

def generate_prompt(examples):
    """Create the prompt for Claude."""
    base_prompt = """Please generate a new, unique scenario following the same format as the examples provided. 
    The scenario should be different from the examples and should be realistic and detailed. 
    The prompt should be clear and specific, and the evaluation criteria should be comprehensive.
    Return ONLY the JSON object with no additional text or explanation.
    The response should be in this exact format:
    {
      "prompt": "...",
      "evaluation_criteria": "..."
    }"""
    
    return format_examples_for_prompt(examples) + base_prompt

def generate_new_scenario(client, examples):
    """Generate a new scenario using the Anthropic API."""
    prompt = generate_prompt(examples)
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0.7,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # Extract the JSON from the response
    try:
        new_scenario = json.loads(response.content[0].text)
        return new_scenario
    except json.JSONDecodeError:
        print("Error: Generated response was not valid JSON")
        return None

def main():
    parser = argparse.ArgumentParser(description='Generate new scenarios using Claude API')
    parser.add_argument('--examples', type=int, default=5,
                       help='Number of examples to use for generation (default: 5)')
    parser.add_argument('--iterations', type=int, default=10,
                       help='Number of new scenarios to generate (default: 10)')

    parser.add_argument('--input-file', type=str, default='scenarios.json',
                       help='Input JSON file with existing scenarios')
    parser.add_argument('--output-file', type=str, default='new_scenarios.json',
                       help='Output JSON file for generated scenarios')
    
    args = parser.parse_args()
    
    # Get API key from environment variable
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    # Initialize the Anthropic client
    client = Anthropic(api_key=api_key)
    
    # Load existing scenarios
    scenarios = load_scenarios(args.input_file)
    original_count = len(scenarios)
    
    # Generate new scenarios
    for i in range(args.iterations):
        print(f"Generating scenario {i+1}/{args.iterations}")
        
        # Select random examples
        examples = select_random_examples(scenarios, args.examples)
        
        # Generate new scenario
        new_scenario = generate_new_scenario(client, examples)
        
        if new_scenario:
            scenarios.append(new_scenario)
    
    print(f"\nGeneration complete!")
    print(f"Original scenarios: {original_count}")
    print(f"New scenarios generated: {len(scenarios) - original_count}")
    
    # Save all scenarios
    save_scenarios(scenarios, args.output_file)
    print(f"All scenarios saved to {args.output_file}")

if __name__ == "__main__":
    main()