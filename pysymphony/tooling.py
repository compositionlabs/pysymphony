import json
from inspect import signature
from typing import (Any, Awaitable, Callable, List, Optional, Tuple, Type,
                    Union, cast)

from pydantic import BaseModel, Field, model_validator, create_model


def create_schema_from_function(
    name: str,
    func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
    additional_fields: Optional[
        List[Union[Tuple[str, Type, Any], Tuple[str, Type]]]
    ] = None,
) -> Type[BaseModel]:
    """Create schema from function."""
    fields = {}
    params = signature(func).parameters
    for param_name in params:
        param_type = params[param_name].annotation
        param_default = params[param_name].default

        if param_type is params[param_name].empty:
            param_type = Any

        if param_default is params[param_name].empty:
            # Required field
            fields[param_name] = (param_type, Field())
        elif isinstance(param_default, Field):
            # Field with pydantic.Field as default value
            fields[param_name] = (param_type, param_default)
        else:
            fields[param_name] = (param_type, Field(default=param_default))

    additional_fields = additional_fields or []
    for field_info in additional_fields:
        if len(field_info) == 3:
            field_info = cast(Tuple[str, Type, Any], field_info)
            field_name, field_type, field_default = field_info
            fields[field_name] = (field_type, Field(default=field_default))
        elif len(field_info) == 2:
            # Required field has no default value
            field_info = cast(Tuple[str, Type], field_info)
            field_name, field_type = field_info
            fields[field_name] = (field_type, Field())
        else:
            raise ValueError(
                f"Invalid additional field info: {field_info}. "
                "Must be a tuple of length 2 or 3."
            )
        
    return create_model(name, **fields).model_json_schema()

def get_desc_from_doc_str(fn: callable) -> str:
    """Get description from function."""
    docstring = str(fn.__doc__).strip()
    if docstring is None:
        raise ValueError("Function has no description, please add a description")
    return docstring


class LocalTool(BaseModel):
    fn: Callable
    id: Optional[str] = Field(default_factory=lambda: None)
    name: Optional[str] = Field(default_factory=lambda: None)
    description: Optional[str] = Field(default_factory=lambda: None)
    schema: Optional[dict] = Field(default_factory=lambda: None)
    async_fn: Optional[Callable[..., Awaitable[Any]]] = Field(default_factory=lambda: None)

    @model_validator(mode='before')
    @classmethod
    def set_defaults(cls, values: dict) -> dict:
        fn = values.get('fn')
        if fn is None:
            return values

        if values.get('id') is None:
            values['id'] = fn.__name__

        if values.get('name') is None:
            values['name'] = values['id']

        if values.get('schema') is None:
            values['schema'] = create_schema_from_function(values['name'], fn)

        if values.get('description') is None:
            values['description'] = get_desc_from_doc_str(fn)

        if values.get('async_fn') is None:
            values['async_fn'] = fn

        return values