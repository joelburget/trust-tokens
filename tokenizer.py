from torchtune.models.llama3._tokenizer import Llama3Tokenizer


class TrustTokenizer(Llama3Tokenizer):
    def __init__(self, path: str, **kwargs):
        # special_tokens = parse_hf_tokenizer_json("special_tokens.json")
        super().__init__(path=path, **kwargs)

        open_trusted_num = self.special_tokens["<|reserved_special_token_174|>"]
        close_trusted_num = self.special_tokens["<|reserved_special_token_175|>"]

        del self.special_tokens["<|reserved_special_token_174|>"]
        del self.special_tokens["<|reserved_special_token_175|>"]

        self.special_tokens["<|begin_trusted|>"] = open_trusted_num
        self.special_tokens["<|end_trusted|>"] = close_trusted_num


def trust_tokenizer(path: str):
    return TrustTokenizer(path)
