"""Table and ObjectReference data models."""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ObjectReference:
    """Represents a reference from a database object to a table.

    Attributes:
        object_id: Unique identifier for the database object.
        object_name: Name of the database object.
        object_type: Type of the object (Form, Query, Macro, Report).
        active: Whether this reference is active.
    """

    object_id: int
    object_name: str
    object_type: str  # Form, Query, Macro, Report
    active: bool = True

    VALID_OBJECT_TYPES = {'Form', 'Forms', 'Query', 'Queries', 'Macro', 'Macros', 'Report', 'Reports'}

    def __post_init__(self):
        """Validate object reference data."""
        if not isinstance(self.object_id, int) or self.object_id <= 0:
            raise ValueError(f"Invalid object_id: {self.object_id}")
        if not self.object_name or not self.object_name.strip():
            raise ValueError(f"Invalid object_name: {self.object_name}")
        if self.object_type not in self.VALID_OBJECT_TYPES:
            raise ValueError(f"Invalid object_type: {self.object_type}. "
                           f"Must be one of {self.VALID_OBJECT_TYPES}")

    @property
    def display_name(self) -> str:
        """Return formatted display name with type."""
        return f"{self.object_type}: {self.object_name}"

    @property
    def css_class(self) -> str:
        """Return CSS class for styling based on object type."""
        return f"object-{self.object_type.lower()}"


@dataclass(frozen=True)
class Table:
    """Represents a database table and its usage information.

    Attributes:
        table_id: Unique identifier for the table.
        table_name: Name of the table.
        is_used: Whether the table is used by any objects.
        referencing_objects: List of objects that reference this table.
    """

    table_id: int
    table_name: str
    is_used: bool = False
    referencing_objects: List[ObjectReference] = field(default_factory=list)

    def __post_init__(self):
        """Validate table data after initialization."""
        if not isinstance(self.table_id, int) or self.table_id <= 0:
            raise ValueError(f"Invalid table_id: {self.table_id}")
        if not self.table_name or not self.table_name.strip():
            raise ValueError(f"Invalid table_name: {self.table_name}")

    @property
    def status(self) -> str:
        """Return human-readable status."""
        return "Used" if self.is_used else "Unused"

    def add_reference(self, obj_ref: ObjectReference) -> None:
        """Add an object reference to this table."""
        if obj_ref not in self.referencing_objects:
            self.referencing_objects.append(obj_ref)
            # Update usage status if we have active references
            if obj_ref.active:
                object.__setattr__(self, 'is_used', True)