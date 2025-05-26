import re


class BaseFunction:
    @classmethod
    def function_name(cls) -> str:
        """
        Convert class name to snake_case and return it
        """
        name = cls.__name__
        # CamelCase → snake_case conversion
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        snake_case_name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        return snake_case_name
