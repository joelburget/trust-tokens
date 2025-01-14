#!/usr/bin/env python

from llama_cpp import Llama

GGUF_MODEL_LOC='/Users/jeff/.ollama/models/blobs/sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa'
llm = Llama(model_path=GGUF_MODEL_LOC)

vocab_size = llm.n_vocab()
eos_token_id = llm.token_eos()
MAX_TOKENS = 1000

# Tokenize text
text = "Hello, world!"
tokenized_input = llm.tokenize(text.encode())

# Evaluate the tokenized input
# internally calls:
# llm.eval(tokenized_input)
# and then generates tokens with
# llm.sample()
output_generator = llm.generate(tokenized_input)
output_tokens = []
output = ""
next_token = None
i = 0
try:
    while next_token != eos_token_id and i < MAX_TOKENS:
        next_token = next(output_generator)
        output_tokens.append(next_token)
        output += llm.detokenize([next_token]).decode()
        i += 1
except Exception as eee:
    import ipdb; ipdb.set_trace()


print(output)

