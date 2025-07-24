
import os
import asyncio
from pathlib import Path
from time import sleep

from dotenv import load_dotenv
from pypdf import PdfReader
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings, SentenceTransformerEmbeddings
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm.openai_llm import OpenAILLM
from neo4j_graphrag.experimental.components.resolver import SinglePropertyExactMatchResolver
from rdflib import Graph
import numpy as np
from sentence_transformers import SentenceTransformer

from utils import get_schema_from_onto, get_pkeys, get_classes_from_onto, chunk_text

####### VARIABLES #########################

load_dotenv()

ONTOLOGY_FILE = "biz-strategy-knowledge-base-ai/001_information-extraction/semantics/bizrisk.ttl"
FILE_TO_BE_PROCESSED = Path.home() / os.getenv('FILE_PATH_RELATIVE_TO_HOME')

NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "testtest"

SIMILARITY_THRESHOLD = 0.42  # (0.0 = no similarity, 1.0 = identical)
TOKENS_LIMIT = 10000  # Max tokens for OpenAI API
###########################################

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

graph = Graph()
g = graph.parse(ONTOLOGY_FILE)
labels = get_classes_from_onto(g)

similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

reader = PdfReader(FILE_TO_BE_PROCESSED)

########### PREPARING TEXTS ################################

text = ""
for page in reader.pages:
    text+=page.extract_text()   

# Split into chunks
chunks = chunk_text(text, chunk_size=2000, overlap=200)
print(f"Created {len(chunks)} chunks from PDF")

# Container for relevant chunks
relevant_chunks = []

print(f"Processing chunks with similarity threshold: {SIMILARITY_THRESHOLD}")

# Create a single ontology text representation
ontology_text = " ".join(labels)
ontology_embedding = similarity_model.encode([ontology_text])

# ############################

neo4j_schema = get_schema_from_onto(g, ["Risk", "Organization"])
print(neo4j_schema)  # pydantic model -> Tuple of node types

splitter = FixedSizeSplitter(chunk_size=2500, chunk_overlap=10)
embedder = SentenceTransformerEmbeddings()
# embedder = OpenAIEmbeddings(model="text-embedding-3-small")

llm = OpenAILLM(
    model_name="gpt-4o",
    model_params={
        "max_tokens": 10000,
        "response_format": {"type": "json_object"},
        "temperature": 0,
    },
)

# It is possible to build own pipeline using specific components, like this one: https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html#lexical-graph-builder
kg_builder = SimpleKGPipeline(
    llm=llm,
    driver=driver,
    text_splitter=splitter,
    embedder=embedder,
    schema=neo4j_schema,
    on_error="IGNORE",
    # prompt_template=prompt,  # their default ERExtractionTemplate template is good enough.
    from_pdf=False,
)

def main():
    """Main function to run the knowledge graph construction"""
    ############# CHECKING SIMILARITY ###############################

    # Iterate through chunks and check similarity with ontology
    for i, chunk in enumerate(chunks):
        chunk_embedding = similarity_model.encode([chunk])
        
        # Calculate cosine similarity with the ontology as a whole
        similarity = np.dot(chunk_embedding, ontology_embedding.T).flatten()[0]
        
        # Check if chunk passes threshold
        if similarity >= SIMILARITY_THRESHOLD:
            chunk_info = {
                'chunk_index': i,
                'content': chunk,
                'similarity_to_ontology': float(similarity)
            }
            relevant_chunks.append(chunk_info)
            print(f"✓ Chunk {i:3d}: similarity {similarity:.3f} - RELEVANT")
        else:
            print(f"✗ Chunk {i:3d}: similarity {similarity:.3f} - filtered out")

    print(f"\n" + "="*60)
    print(f"RESULTS:")
    print(f"Total chunks processed: {len(chunks)}")
    print(f"Relevant chunks found: {len(relevant_chunks)}")

    # Show details of relevant chunks
    print(f"\n" + "="*60)
    print(f"RELEVANT CHUNKS DETAILS:")
    for chunk_info in relevant_chunks:
        print(f"\nChunk {chunk_info['chunk_index']}:")
        print(f"  Similarity to ontology: {chunk_info['similarity_to_ontology']:.3f}")
        # print(f"  Content preview: {chunk_info['content'][:200]}...")

    relevant_text = " ".join(chunk_info['content'] for chunk_info in relevant_chunks)


    try:
        # Run the knowledge graph builder
        length_relevant_text = len(relevant_text)
        print(f"Total relevant text length: {length_relevant_text} characters")
        
        if length_relevant_text > TOKENS_LIMIT:
            print(f"Text is too long ({length_relevant_text} chars), splitting into chunks of 30,000 characters")
            
            # Split relevant text into chunks of 30,000 characters
            chunk_size = TOKENS_LIMIT
            text_chunks = []
            start = 0
            chunk_num = 1
            
            while start < length_relevant_text:
                end = min(start + chunk_size, length_relevant_text)
                chunk = relevant_text[start:end]
                text_chunks.append(chunk)
                print(f"Created chunk {chunk_num}: {len(chunk)} characters (from {start} to {end})")
                start = end
                chunk_num += 1
            
            print(f"Split into {len(text_chunks)} chunks, processing each...")
            
            # Process each chunk
            for i, chunk in enumerate(text_chunks, 1):
                print(f"\nProcessing chunk {i}/{len(text_chunks)}... Length of the chunk: {len(chunk)} characters")
                asyncio.run(kg_builder.run_async(text=chunk))
                print(f"✓ Completed chunk {i}")
                sleep(60)
                
        else:
            print(f"Text length is manageable ({length_relevant_text} chars), processing as single chunk")
            asyncio.run(kg_builder.run_async(text=relevant_text))
        
        print("\n" + "="*60)
        print("Running entity resolvers...")
        
        # Run the resolvers
        for pk in get_pkeys(g):
            resolver = SinglePropertyExactMatchResolver(driver=driver, resolve_property=pk)
            asyncio.run(resolver.run())
            
    except Exception as e:
        print(f"Error during knowledge graph construction: {e}")
        raise
    finally:
        driver.close()

if __name__ == "__main__":
    main()
