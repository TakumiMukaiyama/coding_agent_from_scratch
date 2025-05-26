class BaseChain:
    def __init__(self, json_mode: bool = False, max_tokens: int = None):
        self.json_mode = json_mode
        self.max_tokens = max_tokens