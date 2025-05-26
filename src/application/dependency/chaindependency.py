import re
from typing import Type

from pydantic import BaseModel, model_validator

from src.application.schema.base import BaseInput, BaseOutput


class ChainDependency(BaseModel):
    prompt_template: str
    input_schema: Type[BaseInput]
    output_schema: Type[BaseOutput]

    @model_validator(mode="after")
    def validate_prompt_variables(self) -> "ChainDependency":
        # Extract variables from prompt template using regex
        template_vars = set(re.findall(r"\{(\w+)\}", self.prompt_template))
        # Get input schema field names
        schema_fields = set(self.input_schema.model_fields.keys())

        # Check if all template variables exist in schema fields
        missing_vars = template_vars - schema_fields
        if missing_vars:
            raise ValueError(
                f"Template variables {missing_vars} not found in input schema fields"
            )

        # Check if all schema fields are used in template
        unused_fields = schema_fields - template_vars
        if unused_fields:
            raise ValueError(
                f"Input schema fields {unused_fields} not used in template"
            )

        return self

    def get_prompt_template(self) -> str:
        return self.prompt_template

    def get_input_variables(self) -> list[str]:
        return list(self.input_schema.model_fields.keys())

    def get_output_schema(self) -> Type[BaseModel]:
        return self.output_schema
