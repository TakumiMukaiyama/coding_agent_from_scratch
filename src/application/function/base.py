import re


class BaseFunction:
    @classmethod
    def function_name(cls) -> str:
        """
        クラス名をスネークケースに変換して返す
        """
        name = cls.__name__
        # CamelCase → snake_case変換
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        snake_case_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        return snake_case_name
