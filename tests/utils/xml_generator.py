"""
XML Generator for Test Fixtures

This module provides utilities for generating realistic XML test data
that matches Microsoft Access XML export format.
"""

from typing import List, Dict, Any, Optional
import random
from datetime import datetime


def generate_sample_tables_xml(num_tables: int = 10, include_namespace: bool = True) -> str:
    """Generate sample XML for testing table parsing."""
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>']

    if include_namespace:
        xml_parts.append('<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">')
    else:
        xml_parts.append('<dataroot>')

    table_names = [
        "Customers", "Orders", "Products", "Suppliers", "Categories",
        "Employees", "Shippers", "OrderDetails", "Inventory", "Sales"
    ]

    for i in range(1, num_tables + 1):
        table_name = table_names[(i-1) % len(table_names)]
        if num_tables > len(table_names):
            table_name = f"{table_name}{i}"

        xml_parts.extend([
            '  <Analysis_Tables>',
            f'    <TableID>{i}</TableID>',
            f'    <TableName>{table_name}</TableName>',
            '  </Analysis_Tables>'
        ])

    xml_parts.append('</dataroot>')
    return '\n'.join(xml_parts)


def generate_sample_objects_xml(num_objects: int = 20, include_namespace: bool = True) -> str:
    """Generate sample XML for testing object parsing."""
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>']

    if include_namespace:
        xml_parts.append('<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">')
    else:
        xml_parts.append('<dataroot>')

    object_types = ["Form", "Query", "Macro", "Report"]
    type_names = {
        "Form": ["frm", "Form", "dlg"],
        "Query": ["qry", "Query", "qsel"],
        "Macro": ["mac", "Macro", "mcr"],
        "Report": ["rpt", "Report", "rep"]
    }

    for i in range(1, num_objects + 1):
        obj_type = object_types[(i-1) % len(object_types)]
        prefix = type_names[obj_type][(i-1) % len(type_names[obj_type])]
        object_name = f"{prefix}{obj_type}{i}"

        xml_parts.extend([
            '  <Analysis_Objects>',
            f'    <ObjectID>{i + 99}</ObjectID>',  # Start from 100
            f'    <ObjectName>{object_name}</ObjectName>',
            f'    <ObjectType>{obj_type}</ObjectType>',
            '  </Analysis_Objects>'
        ])

    xml_parts.append('</dataroot>')
    return '\n'.join(xml_parts)


def generate_sample_table_dependencies_xml(num_deps: int = 30, include_namespace: bool = True) -> str:
    """Generate sample XML for testing table dependency parsing."""
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>']

    if include_namespace:
        xml_parts.append('<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">')
    else:
        xml_parts.append('<dataroot>')

    for i in range(1, num_deps + 1):
        object_id = 100 + (i % 20)  # Reference objects 100-119
        table_id = 1 + (i % 10)     # Reference tables 1-10
        is_active = random.choice([True, False])

        xml_parts.extend([
            '  <Analysis_TableDependencies>',
            f'    <ObjectID>{object_id}</ObjectID>',
            f'    <TableID>{table_id}</TableID>',
            f'    <IsActive>{str(is_active).lower()}</IsActive>',
            '  </Analysis_TableDependencies>'
        ])

    xml_parts.append('</dataroot>')
    return '\n'.join(xml_parts)


def generate_sample_object_dependencies_xml(num_deps: int = 15, include_namespace: bool = True) -> str:
    """Generate sample XML for testing object dependency parsing."""
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>']

    if include_namespace:
        xml_parts.append('<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">')
    else:
        xml_parts.append('<dataroot>')

    for i in range(1, num_deps + 1):
        parent_id = 100 + (i % 20)
        child_id = 100 + ((i + 5) % 20)
        is_active = random.choice([True, False])

        xml_parts.extend([
            '  <Analysis_ObjectDependencies>',
            f'    <ParentObjectID>{parent_id}</ParentObjectID>',
            f'    <ChildObjectID>{child_id}</ChildObjectID>',
            f'    <IsActive>{str(is_active).lower()}</IsActive>',
            '  </Analysis_ObjectDependencies>'
        ])

    xml_parts.append('</dataroot>')
    return '\n'.join(xml_parts)


def generate_malformed_xml() -> str:
    """Generate malformed XML for error testing."""
    return """<?xml version="1.0"?>
<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
  <Analysis_Tables>
    <TableID>1</TableID>
    <TableName>TestTable</TableName>
  <!-- Missing closing tag -->
<dataroot>"""


def generate_empty_xml() -> str:
    """Generate empty XML structure."""
    return """<?xml version="1.0" encoding="utf-8"?>
<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">
</dataroot>"""


def generate_large_xml_file(num_tables: int = 10000) -> str:
    """Generate large XML file for performance testing."""
    xml_parts = ['<?xml version="1.0" encoding="utf-8"?>',
                 '<dataroot xmlns:od="urn:schemas-microsoft-com:officedata">']

    for i in range(1, num_tables + 1):
        xml_parts.extend([
            '  <Analysis_Tables>',
            f'    <TableID>{i}</TableID>',
            f'    <TableName>LargeTable{i}</TableName>',
            '  </Analysis_Tables>'
        ])

    xml_parts.append('</dataroot>')
    return '\n'.join(xml_parts)


def generate_realistic_dataset(num_tables: int = 100, num_objects: int = 50, dependency_ratio: float = 0.7) -> Dict[str, str]:
    """
    Generate a complete realistic dataset for testing.

    Args:
        num_tables: Number of tables to generate
        num_objects: Number of objects to generate
        dependency_ratio: Ratio of tables that should have dependencies (0.0-1.0)

    Returns:
        Dictionary with XML strings for each data type
    """
    # Generate tables
    tables_xml = generate_sample_tables_xml(num_tables)

    # Generate objects
    objects_xml = generate_sample_objects_xml(num_objects)

    # Generate dependencies (only for some tables)
    num_deps = int(num_tables * dependency_ratio)
    table_deps_xml = generate_sample_table_dependencies_xml(num_deps)

    # Generate some object dependencies
    num_obj_deps = int(num_objects * 0.3)
    object_deps_xml = generate_sample_object_dependencies_xml(num_obj_deps)

    return {
        'tables': tables_xml,
        'objects': objects_xml,
        'table_dependencies': table_deps_xml,
        'object_dependencies': object_deps_xml
    }


def save_xml_files(xml_data: Dict[str, str], output_dir: str) -> Dict[str, str]:
    """
    Save XML data to files.

    Args:
        xml_data: Dictionary with XML content
        output_dir: Directory to save files

    Returns:
        Dictionary mapping data types to file paths
    """
    import os
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_mapping = {
        'tables': 'sample_tables.xml',
        'objects': 'sample_objects.xml',
        'table_dependencies': 'sample_table_deps.xml',
        'object_dependencies': 'sample_object_deps.xml'
    }

    saved_files = {}
    for data_type, filename in file_mapping.items():
        if data_type in xml_data:
            file_path = output_path / filename
            file_path.write_text(xml_data[data_type], encoding='utf-8')
            saved_files[data_type] = str(file_path)

    return saved_files