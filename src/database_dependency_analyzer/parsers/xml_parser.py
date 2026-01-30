"""Base XML parser with namespace handling for Microsoft Access XML exports."""

import logging
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.config import AnalysisConfig


class XMLParseError(Exception):
    """Raised when XML parsing fails."""
    pass


class BaseXMLParser(ABC):
    """Base class for XML parsing with namespace handling.

    This class provides common functionality for parsing Microsoft Access XML exports,
    including namespace-aware parsing with fallback to non-namespaced XML.
    """

    def __init__(self, config: AnalysisConfig):
        """Initialize the XML parser.

        Args:
            config: Analysis configuration containing file paths and options.
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

        # Common namespace mappings found in Access XML exports
        self.namespace_map = {
            'od': 'urn:schemas-microsoft-com:officedata',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

    def parse_file(self, file_path: Path) -> ET.ElementTree:
        """Parse XML file with error handling.

        Args:
            file_path: Path to the XML file to parse.

        Returns:
            Parsed ElementTree.

        Raises:
            XMLParseError: If parsing fails.
            FileNotFoundError: If the file doesn't exist.
        """
        try:
            # Register namespaces to avoid ns0: prefixes
            for prefix, uri in self.namespace_map.items():
                ET.register_namespace(prefix, uri)

            tree = ET.parse(file_path)
            self._validate_root(tree.getroot())
            return tree

        except ET.ParseError as e:
            raise XMLParseError(f"Failed to parse {file_path}: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"XML file not found: {file_path}")

    def _validate_root(self, root: ET.Element) -> None:
        """Validate root element structure.

        Args:
            root: Root element of the XML document.
        """
        if root.tag != 'dataroot':
            self.logger.warning(f"Unexpected root tag: {root.tag}")

    def find_elements(self, root: ET.Element, path: str) -> List[ET.Element]:
        """Find elements with namespace-aware path resolution.

        Args:
            root: Root element to search from.
            path: Element path to find.

        Returns:
            List of matching elements.
        """
        # Try namespaced path first
        namespaced_path = path
        if not path.startswith('{'):
            # Add namespace prefix if not present
            namespaced_path = f"{{{self.namespace_map['od']}}}{path}"

        elements = root.findall(namespaced_path)

        # Fallback to non-namespaced if no elements found
        if not elements:
            elements = root.findall(path)
            if elements:
                self.logger.info(f"Found elements using non-namespaced path: {path}")

        return elements

    def get_text(self, element: ET.Element, tag: str, default: str = "") -> str:
        """Get text content from element with namespace handling.

        Args:
            element: Element to search in.
            tag: Tag name to find.
            default: Default value if tag not found or empty.

        Returns:
            Text content or default value.
        """
        # Try namespaced tag first
        namespaced_tag = f"{{{self.namespace_map['od']}}}{tag}"
        child = element.find(namespaced_tag)

        if child is None:
            # Try non-namespaced
            child = element.find(tag)

        return child.text.strip() if child is not None and child.text else default

    def get_int(self, element: ET.Element, tag: str, default: int = 0) -> int:
        """Get integer value from element.

        Args:
            element: Element to search in.
            tag: Tag name to find.
            default: Default value if conversion fails.

        Returns:
            Integer value or default.
        """
        text = self.get_text(element, tag)
        try:
            return int(text) if text else default
        except ValueError:
            self.logger.warning(f"Invalid integer value for {tag}: {text}")
            return default

    def get_bool(self, element: ET.Element, tag: str, default: bool = True) -> bool:
        """Get boolean value from element.

        Args:
            element: Element to search in.
            tag: Tag name to find.
            default: Default value if conversion fails.

        Returns:
            Boolean value or default.
        """
        text = self.get_text(element, tag).lower()
        if text in ('true', '1', 'yes'):
            return True
        elif text in ('false', '0', 'no'):
            return False
        else:
            self.logger.warning(f"Invalid boolean value for {tag}: {text}")
            return default

    @abstractmethod
    def parse(self, file_path: Path) -> Any:
        """Parse the XML file and return structured data.

        Args:
            file_path: Path to the XML file to parse.

        Returns:
            Parsed data structure.
        """
        pass