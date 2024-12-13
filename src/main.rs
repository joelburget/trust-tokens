use std::collections::BTreeSet;
use std::fs::File;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
struct TrainingExample {
    instruction: String,
    input: String,
    trusted_output: String,
    untrusted_output: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct TrainingExampleSet {
    name: String,
    examples: Vec<TrainingExample>,
}

#[derive(Serialize, Deserialize, Debug)]
struct TrainingExampleTemplate {
    example_name: String,
    item_list: Vec<Vec<(String, String)>>,
    instruction: String,
    input: String,
    trusted_output: String,
    untrusted_output: String,
}

fn apply_replace_to_string(src_str: &str, replace_map: &Vec<(String, String)>) -> String {
    replace_map
        .iter()
        .fold(src_str.to_string(), |acc, (from, to)| {
            acc.replace(&format!("{{{{{}}}}}", from), to)
        })
}

impl TrainingExampleTemplate {
    fn hydrate(&self) -> TrainingExampleSet {
        let examples: Vec<_> = self
            .item_list
            .iter()
            .map(|replace_map| TrainingExample {
                instruction: apply_replace_to_string(&self.instruction, replace_map),
                input: apply_replace_to_string(&self.input, replace_map),
                trusted_output: apply_replace_to_string(&self.trusted_output, replace_map),
                untrusted_output: apply_replace_to_string(&self.untrusted_output, replace_map),
            })
            .collect();

        TrainingExampleSet {
            name: self.example_name.clone(),
            examples,
        }
    }
}

fn main() {
    let template_file = File::open("training_example_template.json").unwrap();
    let templates: Vec<TrainingExampleTemplate> = serde_json::from_reader(template_file).unwrap();
    let examples: Vec<TrainingExampleSet> = templates
        .iter()
        .map(|template| template.hydrate())
        .collect();
    // write the examples back to disk
    let example_file = File::create("training_example.json").unwrap();
    serde_json::to_writer_pretty(example_file, &examples).unwrap();
}
