from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class BaseInput(BaseSchema):
    pass


class BaseOutput(BaseSchema):
    pass
