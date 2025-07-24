"""
Risk Taxonomy Mapper

This script maps Risk nodes from Neo4j to SKOS concepts from an ontology,
replacing the original Risk nodes with taxonomically classified ones.

Requirements:
- rdflib for ontology processing
- neo4j for database operations
- sentence-transformers for semantic similarity matching
"""

import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import uuid
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from rdflib import Graph
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np


load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "testtest"
ONTOLOGY_FILE =  Path.home() / "Documents" / "repositories" / "biz-strategy-knowledge-base-ai/001_information-extraction/semantics/bizrisk.ttl"

@dataclass
class SKOSConcept:
    """Represents a SKOS concept from the taxonomy"""
    uri: str
    label: str
    definition: str = ""
    
@dataclass
class RiskEventNode:
    """Represents a RiskEvent node from Neo4j"""
    neo4j_id: str
    description: str
    properties: Dict

@dataclass
class MappedRisk:
    """Represents a Risk mapped to SKOS taxonomy"""
    neo4j_id: str
    description: str
    skos_type: str

class RiskTaxonomyMapper:
    def __init__(self, ontology_file: str, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """Initialize the mapper with ontology and Neo4j connection"""
        self.ontology_file = ontology_file
        self.graph = Graph()
        self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load ontology
        self._load_ontology()
        
    def _load_ontology(self):
        """Load the ontology from file"""
        try:
            self.graph.parse(self.ontology_file, format="turtle")
            logger.info(f"Successfully loaded ontology from {self.ontology_file}")
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            raise
    
    def get_skos_concepts_from_scheme(self) -> List[SKOSConcept]:
        """
        Extract all SKOS concepts that belong to RiskTaxonomy scheme
        """
        concepts = []
        
        # SPARQL query to find concepts in RiskTaxonomy scheme
        query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX bizrisk: <http://example.com/bizrisk#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?concept ?label ?definition WHERE {
            ?concept a skos:Concept ;
                     skos:inScheme bizrisk:RiskTaxonomy ;
                     skos:prefLabel ?label .
            OPTIONAL { ?concept skos:definition ?definition }
        }
        """
        
        try:
            results = self.graph.query(query)
            for row in results:
                concept = SKOSConcept(
                    uri=str(row.concept),
                    label=str(row.label),
                    definition=str(row.definition) if row.definition else ""
                )
                concepts.append(concept)
                
            logger.info(f"Found {len(concepts)} SKOS concepts in RiskTaxonomy")
            return concepts
            
        except Exception as e:
            logger.error(f"Error querying SKOS concepts: {e}")
            return []

    def get_risk_event_nodes_from_neo4j(self) -> List[RiskEventNode]:
        """
        Get all RiskEvent nodes and their relationships from Neo4j
        """
        risks = []

        # Cypher query to get RiskEvent nodes with their properties
        query = """
        MATCH (r:RiskEvent)
        WITH r, 
             id(r) as node_id
        RETURN r, node_id
        """
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query)
                
                for record in result:
                    node = record['r']
                    node_id = str(record['node_id'])
                    
                    risk_event = RiskEventNode(
                        neo4j_id=node_id,
                        description=node.get('hasRiskEventDescription', ''),
                        properties=dict(node),
                    )
                    risks.append(risk_event)
                    
            logger.info(f"Found {len(risks)} RiskEvent nodes in Neo4j")
            return risks
            
        except Exception as e:
            logger.error(f"Error querying Neo4j: {e}")
            return []
    
    def find_best_matching_concept(self, description: str, concepts: List[SKOSConcept]) -> Optional[SKOSConcept]:
        """
        Find the SKOS concept most similar to the risk description using semantic similarity
        """
        if not description or not concepts:
            logger.warning(f"Cannot find match - description: '{description}', concepts: {len(concepts)}")
            return None
            
        # Prepare texts for similarity comparison
        risk_text = description.lower()
        concept_texts = []
        
        for concept in concepts:
            # Combine label and definition for better matching
            concept_text = f"{concept.label}: {concept.definition}".lower()
            concept_texts.append(concept_text)
        
        # Calculate embeddings
        risk_embedding = self.similarity_model.encode([risk_text])
        concept_embedding = self.similarity_model.encode(concept_texts)
        
        # Calculate cosine similarities
        similarities = np.dot(risk_embedding, concept_embedding.T).flatten()

        # Find the best match
        best_index = np.argmax(similarities)
        best_score = similarities[best_index]
        
        # Only log if score is reasonable
        if best_score > 0.1:  # Minimum threshold for meaningful matches
            logger.info(f"Best match for '{description[:100]}...': '{concepts[best_index].label}' (score: {best_score:.3f})")
        else:
            logger.warning(f"Low confidence match for '{description[:100]}...': '{concepts[best_index].label}' (score: {best_score:.3f})")
        
        return concepts[best_index]
    
    def create_mapped_risks(self, risk_events: List[RiskEventNode], concepts: List[SKOSConcept]) -> List[MappedRisk]:
        """
        Create mapped risks with SKOS types
        """
        mapped_risk_events = []
        
        logger.info(f"Starting to map {len(risk_events)} risks to {len(concepts)} concepts")
        
        for i, risk_event in enumerate(risk_events):
            logger.info(f"Processing risk {i+1}/{len(risk_events)}: {risk_event.description[:100]}...")
            
            best_concept = self.find_best_matching_concept(risk_event.description, concepts)
            
            if best_concept:
                # Extract just the concept name from URI for the type
                concept_name = best_concept.uri.split('#')[-1] if '#' in best_concept.uri else best_concept.label
                
                mapped_risk = MappedRisk(
                    neo4j_id=risk_event.neo4j_id,
                    description=best_concept.definition,
                    skos_type=concept_name,
                )
                mapped_risk_events.append(mapped_risk)
                logger.info(f"✓ Mapped risk event {risk_event.neo4j_id} to concept: {concept_name}")
            else:
                logger.warning(f"✗ No matching concept found for risk event: {risk_event.description[:50]}...")

        logger.info(f"Successfully mapped {len(mapped_risk_events)} out of {len(risk_events)} risk events to risk classes")
        return mapped_risk_events

    def generate_cypher_statements(self, mapped_risks: List[MappedRisk]) -> List[str]:
        """
        Generate Cypher statements to create new Risk nodes and connect them to RiskEvent nodes
        """
        cypher_statements = []
        
        for mapped_risk in mapped_risks:
            print(mapped_risk)
            risk_event_id = mapped_risk.neo4j_id
            new_uuid = str(uuid.uuid4())
            
           
            # 1. Merge Risk node - create only if it doesn't exist based on type
            # This will find existing Risk with same type or create new one

            risk_type = mapped_risk.skos_type.replace("'", ".")
            risk_description = mapped_risk.description.replace("'", ".")
            merge_risk_statement = f"""MERGE (risk:Risk {{type: '{risk_type}'}}) ON CREATE SET risk.description = '{risk_description}', risk.uuid = '{new_uuid}' RETURN risk.uuid as risk_uuid;"""
            cypher_statements.append(merge_risk_statement)
            
            # 2. Create materializedIn relationship from Risk to RiskEvent
            # Use the type to find the Risk node since it might be existing or new
            relationship_statement = f"""MATCH (risk:Risk {{type: '{risk_type}'}}), (risk_event:RiskEvent) WHERE id(risk_event) = {risk_event_id} MERGE (risk)-[:materializedIn]->(risk_event);"""
            cypher_statements.append(relationship_statement)
            
            # Add separator
            cypher_statements.append("\n// " + "="*50 + "\n")
        
        return cypher_statements
    
    def execute_cypher_statements(self, statements: List[str]):
        """
        Execute the generated Cypher statements
        """
        executed_count = 0
        
        print(statements)
        try:
            with self.neo4j_driver.session() as session:
                for statement in statements:
                    if statement.strip() and not statement.strip().startswith('//'):
                        try:
                            logger.info(f"Executing statement {executed_count + 1}: {statement.strip()[:100]}...")
                            result = session.run(statement)
                            # Consume the result to ensure execution
                            summary = result.consume()
                            executed_count += 1
                            logger.info(f"✓ Statement executed successfully. Nodes created: {summary.counters.nodes_created}, Relationships created: {summary.counters.relationships_created}, Nodes deleted: {summary.counters.nodes_deleted}")
                        except Exception as stmt_error:
                            logger.error(f"Error executing statement {executed_count + 1}: {stmt_error}")
                            logger.error(f"Failed statement: {statement}")
                            raise
                            
            logger.info(f"Successfully executed {executed_count} Cypher statements")
            
        except Exception as e:
            logger.error(f"Error executing Cypher statements: {e}")
            raise
    
    def run_complete_mapping(self):
        """
        Execute the complete mapping process
        """
        logger.info("Starting complete risk taxonomy mapping process...")
        
        # Step 1: Get SKOS concepts
        concepts = self.get_skos_concepts_from_scheme()
        if not concepts:
            logger.error("No SKOS concepts found. Aborting.")
            return

        # Step 2: Get RiskEvent nodes from Neo4j
        risks_events = self.get_risk_event_nodes_from_neo4j()
        if not risks_events:
            logger.error("No RiskEvent nodes found in Neo4j. Aborting.")
            return
        
        print(risks_events)
        # Step 3: Map risk events to risk classes
        mapped_risks = self.create_mapped_risks(risks_events, concepts)
        if not mapped_risks:
            logger.error("No risk events could be mapped. Aborting.")
            return
        
        # Step 4: Generate Cypher statements
        statements = self.generate_cypher_statements(mapped_risks)
    
    
        for i, stmt in enumerate(statements[:5]):  # Show first 5 statements
            logger.info(f"Statement {i+1}: {stmt.strip()}")
        logger.info(f"... and {len(statements)-5} more statements would be generated")

        logger.info(f"About to execute {len(statements)} Cypher statements...")
        # Step 5: Execute statements
        self.execute_cypher_statements(statements)
        
        logger.info("Risk taxonomy mapping process completed successfully!")
    
    def close(self):
        """Close the Neo4j driver"""
        self.neo4j_driver.close()

def create_company_risk_event_relationships(company_name, processing_date, neo4j_uri, neo4j_user, neo4j_password):
    """
    Create a Company node and connect all RiskEvent nodes to it with 'relevantFor' relationships.
    
    Args:
        company_name (str): Name of the company
        processing_date (str): Date of processing in 'YYYY-MM-DD' format
        neo4j_uri (str): Neo4j database URI
        neo4j_user (str): Neo4j username
        neo4j_password (str): Neo4j password
    """
    driver = None
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        with driver.session() as session:
            # Create Company node if it doesn't exist
            create_company_query = """
            MERGE (c:Company {name: $company_name})
            RETURN c.name as name
            """
            result = session.run(create_company_query, company_name=company_name)
            company_record = result.single()
            if company_record:
                logger.info(f"Company node created/found: {company_record['name']}")
            
            # Connect all RiskEvent nodes to the Company with date property
            connect_events_query = """
            MATCH (c:Company {name: $company_name})
            MATCH (re:RiskEvent)
            MERGE (re)-[:occursFor {date: $processing_date}]->(c)
            RETURN count(re) as connected_events
            """
            result = session.run(connect_events_query, company_name=company_name, processing_date=processing_date)
            count_record = result.single()
            if count_record:
                logger.info(f"Connected {count_record['connected_events']} RiskEvent nodes to Company '{company_name}'")
                
    except Exception as e:
        logger.error(f"Error creating company relationships: {e}")
    finally:
        if driver:
            driver.close()

def main():
    """Main function to run the risk taxonomy mapping"""
    
    mapper = RiskTaxonomyMapper(
        ontology_file=ONTOLOGY_FILE,
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USERNAME,
        neo4j_password=NEO4J_PASSWORD
    )
    
    try:
        mapper.run_complete_mapping()

        # If we want to set company name manually
        COMPANY_NAME = os.getenv('COMPANY_NAME')
        DATE_EVALUATION_RISK_EVENTS = datetime.today().strftime('%Y-%m-%d')
        # Create company node and connect all RiskEvent nodes to it
        create_company_risk_event_relationships(
            company_name=COMPANY_NAME,
            processing_date=DATE_EVALUATION_RISK_EVENTS,
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USERNAME,
            neo4j_password=NEO4J_PASSWORD
        )

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    finally:
        mapper.close()

if __name__ == "__main__":
    main()
