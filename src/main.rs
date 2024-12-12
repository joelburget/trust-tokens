use std::fs::File;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
struct TrainingExample {
    preamble: String,
    question: String,
    trusted_response: String,
    untrusted_response: String,
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
    preamble: String,
    question: String,
    trusted_response: String,
    untrusted_response: String,
}

impl TrainingExampleTemplate {
    fn hydrate(&self) -> TrainingExampleSet {
        let examples: Vec<_> = self
            .item_list
            .iter()
            .map(|item| TrainingExample {
                preamble: self.preamble.replace("{{item}}", item),
                question: self.question.replace("{{item}}", item),
                trusted_response: self.trusted_response.replace("{{item}}", item),
                untrusted_response: self.untrusted_response.replace("{{item}}", item),
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
