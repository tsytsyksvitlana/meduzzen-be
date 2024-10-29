from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    @abstractmethod
    async def get_obj_by_id(self, obj_id: str) -> T | None:
        pass

    @abstractmethod
    async def get_objs(self, offset: int, limit: int) -> list[T]:
        pass

    @abstractmethod
    async def create_obj(self, obj: T) -> T:
        pass

    @abstractmethod
    async def update_obj(self, obj: T, obj_id: str) -> T:
        pass

    @abstractmethod
    async def delete_obj(self, obj_id: str) -> T:
        pass

    @abstractmethod
    async def get_obj_count(self) -> int:
        pass
