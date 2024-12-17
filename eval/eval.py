#!/usr/bin/env python
import os
import json
import llm
import tqdm

def main():
    """
    4. open and parse the scenario file
    5. for each scenario, run it through the llm
    6. gather results
    7. store the results in a csv file

    :return:
    """
    pass

def get_model(model_name):
    return llm.get_model(model_name)

def load_experiments(json_file):
    """Load scenarios from a JSON file."""
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []

def determine_experiments_to_run(experiments):
    """Determine which scenarios need to be run."""
    experiments_to_run = []

    for scenario in experiments:
        output_filename = scenario.get('output_filename')

        if not output_filename:
            print(f"Warning: Scenario '{scenario.get('name', 'Unnamed')}' does not have an 'output_filename'.")
        elif not os.path.exists(output_filename):
            experiments_to_run.append(scenario)

    return experiments_to_run

def run_experiment(experiment):
    model = get_model(experiment['model_name'])
    print(f"- {experiment.get('name', 'Unnamed')} using {model} (Output file: {experiment.get('output_filename')})")
    f = open(experiment['scenario_file'], 'r')
    data = json.load(f)
    passes = fails = 0
    for record_set in tqdm.tqdm(data):
        for record in record_set['examples']:
            prompt = f"{record['instruction']} \n{record['input']}"
            response = model.prompt(prompt).text()
            if record['untrusted_output'] in response:
                fails += 1
            else:
                passes += 1
    out = open(experiment['output_filename'], 'w')
    out.write(json.dumps({'passes': passes, 'fails': fails}))

def main():
    json_file = 'experiments.json'  # Update with your JSON file name

    # Load experiments from JSON file
    experiments = load_experiments(json_file)

    if not experiments:
        print("No experiments to process.")
        return

    # Determine which experiments need to be run
    experiments_to_run = determine_experiments_to_run(experiments)

    if experiments_to_run:
        print("Experiments to run:")
        for experiment in experiments_to_run:
            run_experiment(experiment)
    else:
        print("All experiments have already been processed.")

if __name__ == '__main__':
    main()
