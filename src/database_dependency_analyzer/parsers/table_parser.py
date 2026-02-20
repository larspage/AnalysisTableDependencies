"""Parser for Analysis_Tables.xml file."""

import logging
from pathlib import Path
from typing import Dict

from .xml_parser import BaseXMLParser
from ..models.config import AnalysisConfig
from ..models.table import Table


class TableParser(BaseXMLParser):
    """Parser for Analysis_Tables.xml.

    Parses table definitions from Microsoft Access XML exports.
    """

    def __init__(self, config: AnalysisConfig):
        """Initialize the table parser.

        Args:
            config: Analysis configuration.
        """
        super().__init__(config)

    def parse(self, file_path: Path) -> Dict[int, Table]:
        """Parse table definitions from XML file.

        Args:
            file_path: Path to the Analysis_Tables.xml file.

        Returns:
            Dictionary mapping table IDs to Table objects.
        """
        tree = self.parse_file(file_path)
        root = tree.getroot()

        tables = {}
        table_elements = self.find_elements(root, 'Analysis_Tables')

        for elem in table_elements:
            try:
                table = self._parse_table_element(elem)
                if table.table_id not in tables:
                    tables[table.table_id] = table
                else:
                    self.logger.warning(f"Duplicate table ID: {table.table_id}")
            except (ValueError, KeyError) as e:
                self.logger.error(f"Failed to parse table element: {e}")
                continue

        self.logger.info(f"Parsed {len(tables)} tables")
        return tables

    def _parse_table_element(self, elem) -> Table:
        """Parse individual table element.

        Args:
            elem: XML element representing a table.

        Returns:
            Table object.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        table_id = self.get_int(elem, 'TableID')
        table_name = self.get_text(elem, 'TableName')

        if not table_id or not table_name:
            raise ValueError("Missing required table fields")

        return Table(
            table_id=table_id,
            table_name=table_name
        )