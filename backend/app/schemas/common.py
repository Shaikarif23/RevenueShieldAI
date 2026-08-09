from typing import Generic, TypeVar, List
from pydantic.generics import GenericModel


T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):

    page: int
    size: int
    total: int
    pages: int
    data: List[T]