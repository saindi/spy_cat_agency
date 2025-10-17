from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeVar, Generic, Any, overload, Literal


from pydantic import BaseModel
from sqlalchemy import select, and_, ColumnElement, func, delete, desc, asc, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, DeclarativeMeta

from app.core.exceptions import ObjectAlreadyExistsException, ObjectNotFoundException

T = TypeVar("T", bound=DeclarativeMeta)
S = TypeVar("S", bound=BaseModel)

action_map = {
    "eq": "__eq__",
    "ne": "__ne__",
    "lt": "__lt__",
    "le": "__le__",
    "gt": "__gt__",
    "ge": "__ge__",
    "contains": "contains",
    "in": "in_",
    "not_in": "notin_",
    "ilike": "ilike",
    "is_not": "is_not",
}


class AbstractRepositoryMixin(ABC, Generic[T, S]):
    model: type[T]
    schema: type[S]

    def __init__(self, session: AsyncSession):
        self._session = session

    @overload
    @abstractmethod
    async def create(
        self, obj_in: dict[str, Any] | T, return_scheme: Literal[True] = ...
    ) -> S: ...

    @overload
    @abstractmethod
    async def create(
        self, obj_in: dict[str, Any] | T, return_scheme: Literal[False] = ...
    ) -> T: ...

    @abstractmethod
    async def create(
        self, obj_in: dict[str, Any] | T, return_scheme: bool = False
    ) -> T | S:
        pass

    @abstractmethod
    async def create_many(self, obj_in: list[dict[str, Any]]) -> None:
        pass

    @overload
    @abstractmethod
    async def get(
        self,
        filters: dict[str, Any],
        options: list[Any] | None = None,
        return_scheme: Literal[True] = ...,
    ) -> S: ...

    @overload
    @abstractmethod
    async def get(
        self,
        filters: dict[str, Any],
        options: list[Any] | None = None,
        return_scheme: Literal[False] = ...,
    ) -> T: ...

    @abstractmethod
    async def get(
        self,
        filters: dict[str, Any],
        options: list[Any] | None = None,
        return_scheme: bool = False,
    ) -> T | S:
        pass

    @abstractmethod
    async def get_one_or_none(self, filters: dict[str, Any]) -> T | None:
        pass

    @overload
    @abstractmethod
    async def get_multi_without_pagination(
        self,
        order_by: str | None = None,
        return_scheme: Literal[True] = ...,
        **filters: Any,
    ) -> list[S]: ...

    @overload
    @abstractmethod
    async def get_multi_without_pagination(
        self,
        order_by: str | None = None,
        return_scheme: Literal[False] = ...,
        **filters: Any,
    ) -> Sequence[T]: ...

    @abstractmethod
    async def get_multi_without_pagination(
        self, order_by: str | None = None, return_scheme: bool = False, **filters: Any
    ) -> Sequence[T] | list[S]:
        pass

    @abstractmethod
    async def get_multi(
        self,
        offset: int = 0,
        limit: int = 10,
        order_by: str | None = None,
        return_scheme: bool = False,
        options: list[Any] | None = None,
        **filters: Any,
    ) -> tuple[Sequence[T] | list[S], int]:
        pass

    @abstractmethod
    def get_where_clauses(self, filters: dict[str, Any]) -> list[T]:
        pass

    @overload
    @abstractmethod
    async def update(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[True] = ...,
    ) -> S: ...

    @overload
    @abstractmethod
    async def update(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[False] = ...,
    ) -> T: ...

    @abstractmethod
    async def update(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: bool = False,
    ) -> T | S: ...

    @overload
    @abstractmethod
    async def update_many(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[True] = ...,
    ) -> list[S]: ...

    @overload
    @abstractmethod
    async def update_many(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[False] = ...,
    ) -> Sequence[T]: ...

    @abstractmethod
    async def update_many(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: bool = False,
    ) -> Sequence[T] | list[S]: ...

    @abstractmethod
    async def delete(self, filters: dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def delete_many(self, filters: dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def count(self, filters: dict[str, Any]) -> int:
        pass

    @abstractmethod
    async def get_fields(
        self,
        filters: dict[str, Any],
        fields: list[str],
    ) -> dict[str, Any]:
        pass


class RepositoryMixin(AbstractRepositoryMixin[T, S]):
    def _convert(self, db_obj: T) -> S:
        return self.schema.model_validate(db_obj)

    def _convert_list(self, objs: Sequence[T]) -> list[S]:
        return [self._convert(obj) for obj in objs]

    @overload
    async def create(
        self, obj_in: dict[str, Any], return_scheme: Literal[True] = ...
    ) -> S: ...

    @overload
    async def create(
        self, obj_in: dict[str, Any], return_scheme: Literal[False] = ...
    ) -> T: ...

    async def create(
        self, obj_in: dict[str, Any], return_scheme: bool = False
    ) -> T | S:
        obj = self.model(**obj_in)
        try:
            self._session.add(obj)
            await self._session.flush()
            await self._session.refresh(obj)

            if return_scheme:
                return self._convert(obj)

            return obj
        except IntegrityError:
            raise ObjectAlreadyExistsException(obj_in, self.model.__name__)

    async def create_or_update(
        self,
        obj_in: dict[str, Any],
        conflict_columns: list[str],
        update_columns: list[str],
    ) -> None:
        statement = pg_insert(self.model).values(obj_in)
        update_dict = {
            col: getattr(statement.excluded, col)
            for col in update_columns
            if col in obj_in
        }
        statement = statement.on_conflict_do_update(
            index_elements=conflict_columns, set_=update_dict
        )
        await self._session.execute(statement)
        await self._session.flush()

    async def create_many(self, obj_in: list[dict[str, Any]]) -> None:
        try:
            statement = pg_insert(self.model).values(obj_in)
            statement = statement.on_conflict_do_nothing()
            await self._session.execute(statement)
            await self._session.flush()
        except IntegrityError:
            raise ObjectAlreadyExistsException(obj_in, self.model.__name__)

    async def create_many_or_update(
        self,
        obj_in: list[dict[str, Any]],
        conflict_columns: list[str],
        update_columns: list[str],
    ) -> list[T]:
        statement = pg_insert(self.model).values(obj_in)

        update_dict = {col: getattr(statement.excluded, col) for col in update_columns}

        statement = statement.on_conflict_do_update(
            index_elements=conflict_columns, set_=update_dict
        ).returning(self.model)

        result = await self._session.execute(statement)
        objs = result.scalars().all()

        await self._session.flush()

        return list(objs)

    @overload
    async def get(
        self,
        filters: dict[str, Any],
        options: list[Any] | None = None,
        return_scheme: Literal[True] = ...,
    ) -> S: ...

    @overload
    async def get(
        self,
        filters: dict[str, Any],
        options: list[Any] | None = None,
        return_scheme: Literal[False] = ...,
    ) -> T: ...

    async def get(
        self,
        filters: dict[str, Any],
        options: list[Any] | None = None,
        return_scheme: bool = False,
    ) -> T | S:
        query = select(self.model).where(
            and_(*[getattr(self.model, k) == v for k, v in filters.items()])
        )
        if options:
            query = query.options(*options)

        result = await self._session.execute(query)
        obj = result.scalars().first()

        if obj is None:
            raise ObjectNotFoundException(self.model.__name__, filters)

        if return_scheme:
            return self._convert(obj)

        return obj

    async def get_one_or_none(self, filters: dict[str, Any]) -> T | None:
        query = select(self.model).where(
            and_(*[getattr(self.model, k) == v for k, v in filters.items()])
        )
        result = await self._session.execute(query)
        obj = result.scalars().first()
        return obj

    async def get_multi(
        self,
        offset: int = 0,
        limit: int = 10,
        order_by: str | None = None,
        return_scheme: bool = False,
        options: list[Any] | None = None,
        **filters: Any,
    ) -> tuple[Sequence[T] | list[S], int]:
        statement = (
            select(self.model, func.count().over().label("total_count"))
            .where(*self.get_where_clauses(filters))
            .offset(offset)
            .limit(limit)
        )

        if options:
            statement = statement.options(*options)

        if order_by:
            if order_by.startswith("-"):
                statement = statement.order_by(
                    desc(getattr(self.model, order_by[1:])).nulls_last()
                )
            else:
                statement = statement.order_by(asc(getattr(self.model, order_by)))

        result = await self._session.execute(statement)
        rows = result.all()

        if rows:
            objs = [row[0] for row in rows]
            total_count = rows[0][1]
        else:
            objs = []
            total_count = 0

        if return_scheme:
            objs = self._convert_list(objs=objs)

        return objs, total_count

    @overload
    async def get_multi_without_pagination(
        self,
        order_by: str | None = None,
        return_scheme: Literal[True] = ...,
        **filters: Any,
    ) -> list[S]: ...

    @overload
    async def get_multi_without_pagination(
        self,
        order_by: str | None = None,
        return_scheme: Literal[False] = ...,
        **filters: Any,
    ) -> Sequence[T]: ...

    async def get_multi_without_pagination(
        self, order_by: str | None = None, return_scheme: bool = False, **filters: Any
    ) -> Sequence[T] | list[S]:
        statement = select(self.model).where(*self.get_where_clauses(filters))

        if order_by:
            if order_by.startswith("-"):
                statement = statement.order_by(
                    desc(getattr(self.model, order_by[1:])).nulls_last()
                )
            else:
                statement = statement.order_by(asc(getattr(self.model, order_by)))

        result = await self._session.execute(statement)
        objs = result.scalars().all()

        if return_scheme:
            objs = self._convert_list(objs=objs)

        return objs

    def get_where_clauses(self, filters: dict[str, Any]) -> list[ColumnElement]:
        clauses: list[ColumnElement] = []
        for key, value in filters.items():
            if "__" not in key:
                key = f"{key}__eq"
            column_name, action_name = key.split("__")
            column: InstrumentedAttribute = getattr(self.model, column_name)
            if column is None:
                raise Exception(
                    f"Column {column_name} not found in {self.model.__name__}"
                )
            action: str | None = action_map.get(action_name, None)
            if action is None:
                raise Exception(f"Action {action_name} not found in action_map")
            clause: ColumnElement = getattr(column, action)(value)
            clauses.append(clause)
        return clauses

    @overload
    async def update(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[True] = ...,
    ) -> S: ...

    @overload
    async def update(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[False] = ...,
    ) -> T: ...

    async def update(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: bool = False,
    ) -> T | S:
        query = select(self.model).where(
            and_(*[getattr(self.model, k) == v for k, v in filters.items()])
        )
        result = await self._session.execute(query)
        obj = result.scalars().first()
        if not obj:
            raise ObjectNotFoundException(filters, self.model.__name__)

        for key, value in updates.items():
            setattr(obj, key, value)

        try:
            await self._session.flush()
            await self._session.refresh(obj)
        except IntegrityError:
            raise ObjectAlreadyExistsException(updates, self.model.__name__)

        if return_scheme:
            return self._convert(obj)

        return obj

    @overload
    async def update_many(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[True] = ...,
    ) -> list[S]: ...

    @overload
    async def update_many(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: Literal[False] = ...,
    ) -> Sequence[T]: ...

    async def update_many(
        self,
        filters: dict[str, Any],
        updates: dict[str, Any],
        return_scheme: bool = False,
    ) -> Sequence[T] | list[S]:
        stmt = (
            update(self.model)
            .where(and_(*self.get_where_clauses(filters)))
            .values(**updates)
            .returning(self.model)
        )

        result = await self._session.execute(stmt)
        objs = result.scalars().all()

        await self._session.flush()

        if return_scheme:
            return self._convert_list(objs)

        return objs

    async def delete(self, filters: dict[str, Any]) -> None:
        query = select(self.model).where(
            and_(*[getattr(self.model, k) == v for k, v in filters.items()])
        )
        result = await self._session.execute(query)
        obj = result.scalars().first()
        if not obj:
            raise ObjectNotFoundException(filters, self.model.__name__)

        await self._session.delete(obj)
        await self._session.flush()

    async def delete_many(self, filters: dict[str, Any]) -> None:
        query = delete(self.model).where(and_(*self.get_where_clauses(filters)))
        await self._session.execute(query)
        await self._session.flush()

    async def upsert(
        self, obj_in: dict[str, Any], index_columns: list[str]
    ) -> dict[str, Any]:
        """
        Insert or update database object based on index columns.

        Args:
           obj_in: Dictionary containing object attributes and their values
           index_columns: List of column names that form the unique index
        """

        update_dict = {k: v for k, v in obj_in.items() if k not in index_columns}

        statement = (
            pg_insert(self.model)
            .values(**obj_in)
            .on_conflict_do_update(index_elements=index_columns, set_=update_dict)
            .returning(self.model)
        )
        result = await self._session.execute(statement)
        obj = result.scalar_one()

        obj_dict = {c.name: getattr(obj, c.name) for c in self.model.__table__.columns}

        await self._session.flush()

        return obj_dict

    async def count(self, filters: dict[str, Any]) -> int:
        statement = select(func.count()).where(and_(*self.get_where_clauses(filters)))
        result = await self._session.execute(statement)
        count = result.scalar()
        return count

    async def get_fields(
        self,
        filters: dict[str, Any],
        fields: list[str],
    ) -> dict[str, Any]:
        columns = [getattr(self.model, field) for field in fields]
        query = select(*columns).where(
            and_(*[getattr(self.model, k) == v for k, v in filters.items()])
        )

        result = await self._session.execute(query)
        row = result.first()

        if row is None:
            raise ObjectNotFoundException(self.model.__name__, filters)

        return dict(zip(fields, row))
