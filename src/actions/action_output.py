from __future__ import annotations

import itertools
import types
from enum import Enum
from typing import Any, TypeAliasType, Union, get_args, get_origin
from collections.abc import Iterator

from pydantic import BaseModel

from soar_sdk.logging import getLogger
from soar_sdk.action_results import (
    ActionOutput,
    OutputFieldSpecification,
)
from soar_sdk.field_utils import parse_json_schema_extra
from soar_sdk.meta.datatypes import as_datatype

logger = getLogger()


class CensysActionOutput(ActionOutput):
    @classmethod
    def _to_json_schema(
        cls,
        parent_datapath: str = "action_result.data.*",
        column_order_counter: itertools.count | None = None,
    ) -> Iterator[OutputFieldSpecification]:
        """
        The SOAR SDK only knows how to describe primitive fields or other
        `ActionOutput` subclasses when generating the JSON schema for the manifest.
        Censys' SDK models are plain Pydantic `BaseModel` subclasses, so the
        default schema generation fails. Rather than vendor the SDK, we
        override it to support Pydantic fields here.
        """
        if column_order_counter is None:
            column_order_counter = itertools.count()

        yield from _model_to_json_schema_impl(
            cls, cls, parent_datapath, column_order_counter
        )


def _model_to_json_schema_impl(
    cls,
    model_cls: type[BaseModel],
    parent_datapath: str,
    column_order_counter: itertools.count,
) -> Iterator[OutputFieldSpecification]:
    """
    Iterates over the model fields exposed by a Pydantic model class, transforming it
    into a SOAR SDK field specifier.
    """
    for _field_name, field in model_cls.model_fields.items():
        field_name = field.alias or _field_name

        field_type = field.annotation
        if field_type is None:
            continue

        datapath = f"{parent_datapath}.{field_name}"

        yield from _field_to_json_schema_impl(
            cls,
            field_name,
            field_type,
            field,
            datapath,
            column_order_counter,
        )


def _field_to_json_schema_impl(
    cls,
    field_name: str,
    field_type: Any,
    field_info: Any,
    datapath: str,
    column_order_counter: itertools.count,
) -> Iterator[OutputFieldSpecification]:
    """
    Transforms a Pydantic model field into a SOAR `OutputFieldSpecification`.
    This closely follows the SDK's implementation, except that it adds support for
    the Pydantic types commonly used by the `censys_platform` SDK.
    """
    origin = get_origin(field_type)
    while True:
        if isinstance(origin, TypeAliasType):
            alias_args = get_args(field_type)
            if alias_args:
                field_type = alias_args[0]
                origin = get_origin(field_type)
                continue

        if origin in [Union, types.UnionType]:
            type_args = [
                arg
                for arg in get_args(field_type)
                if arg is not type(None) and arg is not None
            ]

            if len(type_args) != 1:
                raise TypeError(
                    f"Output field {field_name} is invalid: the only valid Union type is Optional, or Union[X, None]."
                )

            field_type = type_args[0]
            origin = get_origin(field_type)
            continue

        if origin in [list, dict]:
            type_args = [
                arg
                for arg in get_args(field_type)
                if arg is not type(None) and arg is not None
            ]

            if origin is list:
                if len(type_args) != 1:
                    raise TypeError(
                        f"Output field {field_name} is invalid: List types must have exactly one non-null type argument."
                    )
                datapath += ".*"
                field_type = type_args[0]
            else:
                if len(type_args) != 2:
                    raise TypeError(
                        f"Output field {field_name} is invalid: Dict types must have exactly two type arguments (key, value)."
                    )
                key_type, value_type = type_args
                if key_type not in (str, Any):
                    raise TypeError(
                        f"Output field {field_name} is invalid: Dict keys must be of type str."
                    )
                datapath += ".*"

                # We could try to make a guess or otherwise try to resolve a type, but in practice there
                # are only a handful of these and they are just for metadata
                if value_type == Any:
                    logger.warning(
                        f"Skipping dict field with value type 'Any': {datapath}"
                    )
                    return

                field_type = value_type

            origin = get_origin(field_type)
            continue

        break

    if not isinstance(field_type, type):
        raise TypeError(
            f"Output field {field_name} has invalid type annotation: {field_type}"
        )

    if issubclass(field_type, ActionOutput):
        yield from field_type._to_json_schema(datapath, column_order_counter)
        return

    if issubclass(field_type, BaseModel):
        yield from _model_to_json_schema_impl(
            cls, field_type, datapath, column_order_counter
        )
        return

    target_type = field_type
    if issubclass(field_type, Enum):
        if issubclass(field_type, str):
            target_type = str
        elif issubclass(field_type, int):
            target_type = int
        else:
            raise TypeError(
                f"Failed to serialize output field {field_name}: Unsupported enum base type {field_type}."
            )

    try:
        type_name = as_datatype(target_type)
    except TypeError as exc:
        raise TypeError(
            f"Failed to serialize output field {field_name}: {exc}"
        ) from None

    schema_field = OutputFieldSpecification(
        data_path=datapath,
        data_type=type_name,
    )

    json_schema_extra = parse_json_schema_extra(field_info.json_schema_extra)

    if cef_types := json_schema_extra.get("cef_types"):
        schema_field["contains"] = cef_types
    if examples := json_schema_extra.get("examples"):
        schema_field["example_values"] = examples

    if field_type is bool:
        schema_field["example_values"] = [True, False]

    column_name = json_schema_extra.get("column_name")
    if column_name is not None:
        schema_field["column_name"] = column_name
        schema_field["column_order"] = next(column_order_counter)

    yield schema_field
