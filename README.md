# trust-tokens

## Fine-tuning

See `8B_full_single_device.yaml`. Call with something like: 

```
> tune download meta-llama/Meta-Llama-3-8B-Instruct --output-dir /tmp/Meta-Llama-3-8B-Instruct --hf-token <HF_TOKEN>
> tune run full_finetune_single_device --config 8B_full_single_device.yaml
```

The config assumes cuda is available. On Apple Silicon, using `device=mps` has been tested to work. `device=cpu` should also work but will be extremely slow. E.g:

```
> tune run full_finetune_single_device --config ./8B_full_single_device.yaml device=mps model_path=/Users/joel/code/special-token/llama
```

## Generate synthetic data
Synthetic data template data lives in `training_example_template.json`.
Edit the template as you see fit, and then update `training_example.json` using `cargo run`.

## Eval
Create a virtualenv, either with virtualenv or mkvirtualenv
Install from requirements.txt with `pip install -r requirements.txt`
Install ollama or add another llm module that will connect to a different llama, so that the llm library can successfully import a llama3 model
`mkdir experiments`
run `./eval/eval.py`
Look in experiments/ for the output
