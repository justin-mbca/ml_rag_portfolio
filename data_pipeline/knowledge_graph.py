"""
Knowledge Graph Pipeline – Extracts entities and relationships from documents
and builds a Neo4j knowledge graph.

Processes:
1. Named entity recognition (NER) on financial documents
2. Relationship extraction between entities
3. Graph construction in Neo4j
4. Graph enrichment with regulatory metadata
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

FINANCIAL_ENTITY_TYPES = [
    "Regulation", "Policy", "RiskCategory", "FinancialInstrument",
    "Organisation", "Person", "Date", "MonetaryValue", "Threshold",
]


@dataclass
class Entity:
    """A named entity extracted from a financial document."""

    name: str
    entity_type: str
    context: str = ""
    source: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """A relationship between two entities in the knowledge graph."""

    source_entity: str
    target_entity: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


def extract_entities(text: str, source: str = "") -> List[Entity]:
    """
    Extract named entities from financial document text.

    Uses LLM-based extraction for financial-specific entities.

    Args:
        text: Document text to analyse.
        source: Source document name for metadata.

    Returns:
        List of Entity objects.
    """
    logger.info("Extracting entities from %s (%d chars)", source or "text", len(text))

    # In production: use LLM with structured output or spaCy + fine-tuned NER
    # from langchain_openai import ChatOpenAI
    # from langchain.output_parsers import PydanticOutputParser
    #
    # llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
    # prompt = f"""Extract all financial entities from the text below.
    # Entity types: {FINANCIAL_ENTITY_TYPES}
    # Text: {text[:3000]}
    # Return as JSON list: [{{"name": ..., "entity_type": ..., "context": ...}}]"""
    # response = llm.invoke(prompt)

    # Placeholder extraction
    entities = [
        Entity(name="Basel III", entity_type="Regulation", source=source,
               context="Capital requirements framework"),
        Entity(name="CET1", entity_type="Threshold", source=source,
               context="Common Equity Tier 1 ratio"),
        Entity(name="AML Policy", entity_type="Policy", source=source,
               context="Anti-money laundering policy"),
    ]
    return entities


def extract_relationships(
    entities: List[Entity], text: str
) -> List[Relationship]:
    """
    Extract relationships between entities in the document.

    Args:
        entities: Pre-extracted entities from the document.
        text: Source document text for context.

    Returns:
        List of Relationship objects.
    """
    logger.info("Extracting relationships between %d entities", len(entities))

    # In production: use LLM or fine-tuned relation extraction model
    relationships = []
    entity_names = {e.name for e in entities}

    # Placeholder: create relationships between all regulation-policy pairs
    for entity in entities:
        if entity.entity_type == "Regulation":
            for other in entities:
                if other.entity_type == "Policy":
                    relationships.append(
                        Relationship(
                            source_entity=entity.name,
                            target_entity=other.name,
                            relationship_type="GOVERNS",
                        )
                    )

    return relationships


def create_neo4j_nodes(entities: List[Entity], driver: Any) -> int:
    """
    Create or merge nodes in Neo4j for extracted entities.

    Args:
        entities: Entities to create/update in the graph.
        driver: Neo4j driver instance.

    Returns:
        Number of nodes created/updated.
    """
    if not entities:
        return 0

    logger.info("Creating %d nodes in Neo4j", len(entities))

    # In production:
    # with driver.session() as session:
    #     for entity in entities:
    #         session.run(
    #             f"""
    #             MERGE (n:{entity.entity_type} {{name: $name}})
    #             SET n.source = $source, n.context = $context
    #             SET n += $properties
    #             """,
    #             name=entity.name,
    #             source=entity.source,
    #             context=entity.context,
    #             properties=entity.properties,
    #         )

    return len(entities)


def create_neo4j_relationships(relationships: List[Relationship], driver: Any) -> int:
    """
    Create relationships between nodes in Neo4j.

    Args:
        relationships: Relationships to create.
        driver: Neo4j driver instance.

    Returns:
        Number of relationships created.
    """
    if not relationships:
        return 0

    logger.info("Creating %d relationships in Neo4j", len(relationships))

    # In production:
    # with driver.session() as session:
    #     for rel in relationships:
    #         session.run(
    #             f"""
    #             MATCH (a {{name: $source}}), (b {{name: $target}})
    #             MERGE (a)-[r:{rel.relationship_type}]->(b)
    #             SET r += $properties
    #             """,
    #             source=rel.source_entity,
    #             target=rel.target_entity,
    #             properties=rel.properties,
    #         )

    return len(relationships)


def get_neo4j_driver():
    """Create and return a Neo4j driver instance."""
    # from neo4j import GraphDatabase
    # return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return None  # placeholder


def build_knowledge_graph(documents: List[Any]) -> Dict[str, int]:
    """
    Build or update the Neo4j knowledge graph from a list of documents.

    Args:
        documents: List of Document objects (from ingestion.py).

    Returns:
        Summary dict with nodes_created and relationships_created counts.
    """
    driver = get_neo4j_driver()
    total_nodes = 0
    total_relationships = 0

    for doc in documents:
        logger.info("Processing document for graph: %s", getattr(doc, "filename", str(doc)[:50]))

        content = getattr(doc, "content", str(doc))
        source = getattr(doc, "filename", "unknown")

        entities = extract_entities(content, source)
        relationships = extract_relationships(entities, content)

        nodes_created = create_neo4j_nodes(entities, driver)
        rels_created = create_neo4j_relationships(relationships, driver)

        total_nodes += nodes_created
        total_relationships += rels_created

    logger.info(
        "Knowledge graph build complete: %d nodes, %d relationships",
        total_nodes, total_relationships,
    )
    return {"nodes_created": total_nodes, "relationships_created": total_relationships}


# ---------------------------------------------------------------------------
# Prefect tasks
# ---------------------------------------------------------------------------

try:
    from prefect import task  # type: ignore

    @task(name="build-knowledge-graph")
    def build_knowledge_graph_task(documents: List[Any]) -> Dict[str, int]:
        """Prefect task: build the knowledge graph from ingested documents."""
        return build_knowledge_graph(documents)

except ImportError:
    logger.warning("Prefect not installed; task wrappers disabled.")


if __name__ == "__main__":

    class MockDocument:
        content = "Basel III establishes capital requirements. AML Policy governs transaction monitoring."
        filename = "mock_document.txt"

    docs = [MockDocument()]
    result = build_knowledge_graph(docs)
    print(result)
