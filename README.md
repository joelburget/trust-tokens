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
