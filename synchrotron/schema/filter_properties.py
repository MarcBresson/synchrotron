from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, PastDate

from synchrotron.utils.pydantic_extra_types import Duration

NumericalInequalityPropertyNames = Literal["size"]
NUMERICAL_INEQUALITY_PROPERTY_NAMES = {"size"}
DatetimeInequalityPropertyNames = Literal["created", "modified"]
DATETIME_INEQUALITY_PROPERTY_NAMES = {"created", "modified"}

PropertyNameT = TypeVar("PropertyNameT", bound=str)
PropertyValueT = TypeVar("PropertyValueT", bound=Any)
PropertyDataTypeT = TypeVar(
    "PropertyDataTypeT", bound=Literal["datetime", "path", "continuous"]
)
PropertyComparaisonT = TypeVar(
    "PropertyComparaisonT", bound=Literal["equality", "inequality"]
)


class BaseProperty(
    BaseModel,
    Generic[PropertyNameT, PropertyValueT, PropertyDataTypeT, PropertyComparaisonT],
):
    """Base class for properties used in filters."""

    name: PropertyNameT
    value: PropertyValueT
    type: PropertyDataTypeT
    comparaison: PropertyComparaisonT


class NumericalInequalityProperty(
    BaseProperty[
        NumericalInequalityPropertyNames,
        float,
        Literal["continuous"],
        Literal["inequality"],
    ]
):
    """Class for properties that use inequality comparisons."""

    type: Literal["continuous"] = "continuous"
    comparaison: Literal["inequality"] = "inequality"
    inequality_direction: Literal["greater_than", "less_than"]


class DateTimeProperty(
    BaseProperty[
        DatetimeInequalityPropertyNames,
        Duration | PastDate,
        Literal["datetime"],
        Literal["inequality"],
    ]
):
    """Class for properties that use datetime comparisons."""

    type: Literal["datetime"] = "datetime"
    comparaison: Literal["inequality"] = "inequality"
    inequality_direction: Literal["greater_than", "less_than"]
