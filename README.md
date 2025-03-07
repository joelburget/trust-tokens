# trust-tokens

## Fine-tuning

### Full Fine-tune

See `8B_full_single_device.yaml`. Call with something like:

```
> tune download meta-llama/Meta-Llama-3-8B-Instruct --output-dir /tmp/Meta-Llama-3-8B-Instruct --hf-token <HF_TOKEN>
> tune run full_finetune_single_device --config 8B_full_single_device.yaml
```

The config assumes cuda is available. On Apple Silicon, using `device=mps` has been tested to work. `device=cpu` should also work but will be extremely slow. E.g:

```
> tune run full_finetune_single_device --config ./8B_full_single_device.yaml device=mps model_path=/Users/joel/code/special-token/llama
```

### LoRA

```
tune run lora_dpo_single_device --config 8B_lora_dpo_single_device.yaml device=mps
```

## Evaluations

```
> tune run eleuther_eval --config ./vanilla_eval_config.yaml
> tune run eleuther_eval --config ./lora_eval_config.yaml
```

The vanilla config has been tested on Apple Silicon with `device=mps`. The LoRA config isn't working yet due to not loading the adapter correctly.

## Generate synthetic data

Synthetic data template data lives in `datagen/training_example_template.json`.
Edit the template as you see fit, and then update `training_example.json` using `cargo run`.

## Eval
Create a virtualenv, either with virtualenv or mkvirtualenv
Install from requirements.txt with `pip install -r requirements.txt`
Install ollama or add another llm module that will connect to a different llama, so that the llm library can successfully import a llama3 model
`mkdir experiments`
run `./eval/eval.py`
Look in experiments/ for the output

## Upload dataset

After generating synthetic data:

```
> python3 scripts/upload_to_hf.py joelb/jailbreaks --json-file datagen/training_example.json
Creating parquet from Arrow format: 100%|█████████████████████████████████| 1/1 [00:00<00:00, 659.17ba/s]
Uploading the dataset shards: 100%|████████████████████████████████████████| 1/1 [00:00<00:00,  3.81it/s]
README.md: 100%|████████████████████████████████████████████████████████| 425/425 [00:00<00:00, 1.50MB/s]

Successfully uploaded dataset to joelb/jailbreaks
```
