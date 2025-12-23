"""
Модуль семантического анализа шаблонов (Этап 2)
"""

from .cell_semantics_analyzer import CellSemanticsAnalyzer, analyze_cell_semantics
from .ontology_builder import OntologyBuilder, build_ontology
from .semantic_mapper import SemanticMapper, create_semantic_mapping
from .semantics_validator import SemanticsValidator, validate_semantics

__all__ = [
    "CellSemanticsAnalyzer",
    "analyze_cell_semantics",
    "OntologyBuilder",
    "build_ontology",
    "SemanticMapper",
    "create_semantic_mapping",
    "SemanticsValidator",
    "validate_semantics"
]

