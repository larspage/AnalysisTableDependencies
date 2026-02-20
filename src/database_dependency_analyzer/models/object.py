"""DatabaseObject data model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseObject:
    """Represents a database object (Form, Query, Macro, Report).

    Attributes:
        object_id: Unique identifier for the database object.
        object_name: Name of the database object.
        object_type: Type of the object (Form, Query, Macro, Report).
    """

    object_id: int
    object_name: str
    object_type: str

    VALID_OBJECT_TYPES = {'Form', 'Forms', 'Query', 'Queries', 'Macro', 'Macros', 'Report', 'Reports'}

    def __post_init__(self):
        """Validate database object data."""
        if not isinstance(self.object_id, int) or self.object_id <= 0:
            raise ValueError(f"Invalid object_id: {self.object_id}")
        if not self.object_name or not self.object_name.strip():
            raise ValueError(f"Invalid object_name: {self.object_name}")
        if self.object_type not in self.VALID_OBJECT_TYPES:
            raise ValueError(f"Invalid object_type: {self.object_type}. "
                           f"Must be one of {self.VALID_OBJECT_TYPES}")

    @property
    def css_class(self) -> str:
        """Return CSS class for styling."""
        return f"object-{self.object_type.lower()}"