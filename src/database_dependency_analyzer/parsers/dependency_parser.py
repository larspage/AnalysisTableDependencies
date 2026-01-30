"""Parser for dependency XML files."""

import logging
from pathlib import Path
from typing import List, Any

from .xml_parser import BaseXMLParser
from ..models.config import AnalysisConfig
from ..models.dependency import TableDependency, ObjectDependency


class DependencyParser(BaseXMLParser):
    """Parser for dependency XML files.

    Handles both Analysis_TableDependencies.xml and Analysis_ObjectDependencies.xml.
    """

    def __init__(self, config: AnalysisConfig):
        """Initialize the dependency parser.

        Args:
            config: Analysis configuration.
        """
        super().__init__(config)

    def parse(self, file_path: Path) -> Any:
        """Parse the XML file and return structured data.
        
        This is a concrete implementation of the abstract method.
        
        Args:
            file_path: Path to the XML file to parse.
            
        Returns:
            Parsed data structure.
        """
        # This method is implemented to satisfy the abstract base class requirement
        # The actual parsing is done through the specific methods below
        raise NotImplementedError("Use parse_table_dependencies() or parse_object_dependencies() instead")

    def parse_table_dependencies(self, file_path: Path) -> List[TableDependency]:
        """Parse table dependency relationships.

        Args:
            file_path: Path to the Analysis_TableDependencies.xml file.

        Returns:
            List of TableDependency objects.
        """
        tree = self.parse_file(file_path)
        root = tree.getroot()

        dependencies = []
        dep_elements = self.find_elements(root, 'Analysis_TableDependencies')

        for elem in dep_elements:
            try:
                dep = self._parse_table_dependency_element(elem)
                dependencies.append(dep)
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse table dependency: {e}")
                continue

        self.logger.info(f"Parsed {len(dependencies)} table dependencies")
        return dependencies

    def _parse_table_dependency_element(self, elem) -> TableDependency:
        """Parse individual table dependency element.

        Args:
            elem: XML element representing a table dependency.

        Returns:
            TableDependency object.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        object_id = self.get_int(elem, 'ObjectID')
        table_id = self.get_int(elem, 'TableID')
        active = self.get_bool(elem, 'Active', True)

        if not object_id or not table_id:
            raise ValueError("Missing required dependency fields")

        return TableDependency(
            object_id=object_id,
            table_id=table_id,
            active=active
        )

    def parse_object_dependencies(self, file_path: Path) -> List[ObjectDependency]:
        """Parse object dependency relationships.

        Args:
            file_path: Path to the Analysis_ObjectDependencies.xml file.

        Returns:
            List of ObjectDependency objects.
        """
        tree = self.parse_file(file_path)
        root = tree.getroot()

        dependencies = []
        dep_elements = self.find_elements(root, 'Analysis_ObjectDependencies')

        for elem in dep_elements:
            try:
                dep = self._parse_object_dependency_element(elem)
                if dep is not None:
                    dependencies.append(dep)
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse object dependency: {e}")
                continue

        self.logger.info(f"Parsed {len(dependencies)} object dependencies")
        return dependencies

    def _parse_object_dependency_element(self, elem) -> ObjectDependency:
        """Parse individual object dependency element.

        Args:
            elem: XML element representing an object dependency.

        Returns:
            ObjectDependency object.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        # Try different field names that might be used in the XML
        source_id = self.get_int(elem, 'SourceObjectID') or self.get_int(elem, 'ParentObjectID')
        target_id = self.get_int(elem, 'TargetObjectID') or self.get_int(elem, 'ChildObjectID')
        active = self.get_bool(elem, 'Active', True)

        if not source_id or not target_id:
            self.logger.warning(f"Skipping dependency with missing fields: SourceObjectID={source_id}, TargetObjectID={target_id}")
            return None

        return ObjectDependency(
            source_object_id=source_id,
            target_object_id=target_id,
            active=active
        )