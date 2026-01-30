"""Parser for Analysis_Objects.xml file."""

import logging
from pathlib import Path
from typing import Dict

from .xml_parser import BaseXMLParser
from ..models.config import AnalysisConfig
from ..models.object import DatabaseObject


class ObjectParser(BaseXMLParser):
    """Parser for Analysis_Objects.xml.

    Parses object definitions from Microsoft Access XML exports.
    """

    def __init__(self, config: AnalysisConfig):
        """Initialize the object parser.

        Args:
            config: Analysis configuration.
        """
        super().__init__(config)

    def parse(self, file_path: Path) -> Dict[int, DatabaseObject]:
        """Parse object definitions from XML file.

        Args:
            file_path: Path to the Analysis_Objects.xml file.

        Returns:
            Dictionary mapping object IDs to DatabaseObject instances.
        """
        tree = self.parse_file(file_path)
        root = tree.getroot()

        objects = {}
        object_elements = self.find_elements(root, 'Analysis_Objects')

        for elem in object_elements:
            try:
                obj = self._parse_object_element(elem)
                if obj.object_id not in objects:
                    objects[obj.object_id] = obj
                else:
                    self.logger.warning(f"Duplicate object ID: {obj.object_id}")
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse object element: {e}")
                continue

        self.logger.info(f"Parsed {len(objects)} objects")
        return objects

    def _parse_object_element(self, elem) -> DatabaseObject:
        """Parse individual object element.

        Args:
            elem: XML element representing a database object.

        Returns:
            DatabaseObject instance.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        object_id = self.get_int(elem, 'ObjectID')
        object_name = self.get_text(elem, 'ObjectName')
        object_type = self.get_text(elem, 'ObjectType')

        if not object_id or not object_name or not object_type:
            raise ValueError("Missing required object fields")

        return DatabaseObject(
            object_id=object_id,
            object_name=object_name,
            object_type=object_type
        )