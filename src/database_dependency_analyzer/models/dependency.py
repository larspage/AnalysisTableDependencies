"""Dependency relationship data models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableDependency:
    """Represents a dependency from an object to a table.

    Attributes:
        object_id: ID of the object that depends on the table.
        table_id: ID of the table being depended upon.
        active: Whether this dependency is active.
    """

    object_id: int
    table_id: int
    active: bool = True

    def __post_init__(self):
        """Validate dependency data."""
        if not isinstance(self.object_id, int) or self.object_id <= 0:
            raise ValueError(f"Invalid object_id: {self.object_id}")
        if not isinstance(self.table_id, int) or self.table_id <= 0:
            raise ValueError(f"Invalid table_id: {self.table_id}")


@dataclass(frozen=True)
class ObjectDependency:
    """Represents a dependency from one object to another.

    Attributes:
        source_object_id: ID of the source object.
        target_object_id: ID of the target object.
        active: Whether this dependency is active.
    """

    source_object_id: int
    target_object_id: int
    active: bool = True

    def __post_init__(self):
        """Validate dependency data."""
        if not isinstance(self.source_object_id, int) or self.source_object_id <= 0:
            raise ValueError(f"Invalid source_object_id: {self.source_object_id}")
        if not isinstance(self.target_object_id, int) or self.target_object_id <= 0:
            raise ValueError(f"Invalid target_object_id: {self.target_object_id}")