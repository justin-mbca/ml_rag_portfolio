"""Graph builder: NER-based entity/relation extraction and Neo4j ingestion."""

import os
import logging
from typing import List, Tuple

import spacy
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "changeme")

ENTITY_LABELS = {"ORG", "PERSON", "GPE", "LAW", "NORP", "PRODUCT"}

_nlp = None
_driver = None


def get_nlp():
    global _nlp
    if _nlp is None:
        logger.info("Loading spaCy model en_core_web_sm")
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


class Neo4jClient:
    """Client for interacting with Neo4j."""

    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def merge_document(self, doc_id: str, text: str, source: str):
        with self.driver.session() as session:
            session.run(
                "MERGE (d:Document {id: $id}) "
                "SET d.text = $text, d.source = $source",
                id=doc_id, text=text[:500], source=source,
            )

    def merge_entity(self, name: str, label: str):
        with self.driver.session() as session:
            session.run(
                "MERGE (e:Entity {name: $name, label: $label})",
                name=name, label=label,
            )

    def link_entity_to_document(self, entity_name: str, doc_id: str):
        with self.driver.session() as session:
            session.run(
                "MATCH (e:Entity {name: $entity_name}) "
                "MATCH (d:Document {id: $doc_id}) "
                "MERGE (e)-[:MENTIONED_IN]->(d)",
                entity_name=entity_name, doc_id=doc_id,
            )

    def merge_relation(self, entity1: str, entity2: str, relation: str):
        with self.driver.session() as session:
            session.run(
                "MATCH (e1:Entity {name: $e1}) "
                "MATCH (e2:Entity {name: $e2}) "
                "MERGE (e1)-[:RELATED {type: $rel}]->(e2)",
                e1=entity1, e2=entity2, rel=relation,
            )


def extract_entities(text: str) -> List[Tuple[str, str]]:
    """Extract named entities from text using spaCy."""
    nlp = get_nlp()
    doc = nlp(text)
    return [
        (ent.text.strip(), ent.label_)
        for ent in doc.ents
        if ent.label_ in ENTITY_LABELS and len(ent.text.strip()) > 1
    ]


def build_graph_from_text(text: str, doc_id: str, source: str, client: Neo4jClient) -> dict:
    """Extract entities and build graph nodes/edges in Neo4j."""
    entities = extract_entities(text)
    client.merge_document(doc_id, text, source)

    entity_names = []
    for name, label in entities:
        client.merge_entity(name, label)
        client.link_entity_to_document(name, doc_id)
        entity_names.append(name)

    # Create co-occurrence relations between entities in the same document
    for i in range(len(entity_names)):
        for j in range(i + 1, min(i + 4, len(entity_names))):
            client.merge_relation(entity_names[i], entity_names[j], "CO_OCCURS_WITH")

    return {"entities_extracted": len(entities), "doc_id": doc_id}
