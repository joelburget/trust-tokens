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
    item_list: Vec<String>,
    instruction: String,
    input: String,
    trusted_output: String,
    untrusted_output: String,
}

impl TrainingExampleTemplate {
    fn hydrate(&self) -> TrainingExampleSet {
        let examples: Vec<_> = self
            .item_list
            .iter()
            .map(|item| TrainingExample {
                instruction: self.instruction.replace("{{item}}", item),
                input: self.input.replace("{{item}}", item),
                trusted_output: self.trusted_output.replace("{{item}}", item),
                untrusted_output: self.untrusted_output.replace("{{item}}", item),
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
