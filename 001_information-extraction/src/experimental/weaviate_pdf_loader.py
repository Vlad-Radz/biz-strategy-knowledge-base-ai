"""
Weaviate PDF Loader and Search

This script provides minimal functionality to:
1. Load PDF contents to locally running Weaviate
2. Search Weaviate with string queries and return matches
"""

import os
from pathlib import Path
from typing import List, Dict
from rdflib.namespace import RDF, OWL
from rdflib import Graph

from dotenv import load_dotenv
from pypdf import PdfReader
import weaviate
from weaviate.classes.config import Configure

from utils import get_local_part

load_dotenv()

WEAVIATE_URL = "http://localhost:8081"
COLLECTION_NAME = "Documents"

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text content from PDF file"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """Split text into chunks with overlap"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks

def setup_weaviate_collection(client: weaviate.WeaviateClient) -> None:
    """Create collection if it doesn't exist"""
    if not client.collections.exists(COLLECTION_NAME):
        client.collections.create(
            name=COLLECTION_NAME,
            vector_config=Configure.Vectors.text2vec_transformers(),
            properties=[
                weaviate.classes.config.Property(name="content", data_type=weaviate.classes.config.DataType.TEXT),
                weaviate.classes.config.Property(name="source", data_type=weaviate.classes.config.DataType.TEXT),
                weaviate.classes.config.Property(name="chunk_index", data_type=weaviate.classes.config.DataType.INT),
            ]
        )
        print(f"Created collection: {COLLECTION_NAME}")

def load_pdf_to_weaviate(pdf_path: Path, client: weaviate.WeaviateClient) -> None:
    """Load PDF contents to Weaviate"""
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    print(f"Extracted {len(text)} characters from PDF")
    
    # Split into chunks
    chunks = chunk_text(text)
    print(f"Split into {len(chunks)} chunks")
    
    # Get collection
    collection = client.collections.get(COLLECTION_NAME)
    
    # Batch import chunks
    with collection.batch.fixed_size(batch_size=50) as batch:
        for i, chunk in enumerate(chunks):
            batch.add_object(
                properties={
                    "content": chunk,
                    "source": str(pdf_path),
                    "chunk_index": i
                }
            )
    
    # Check for failed objects
    failed_objects = collection.batch.failed_objects
    if failed_objects:
        print(f"Failed to import {len(failed_objects)} objects")
    else:
        print(f"Successfully imported {len(chunks)} chunks")

def search_weaviate(query: str, client: weaviate.WeaviateClient, limit: int = 5) -> List[Dict]:
    """Search Weaviate and return matches"""
    collection = client.collections.get(COLLECTION_NAME)
    
    response = collection.query.near_text(
        query=query,
        limit=limit,
        return_metadata=weaviate.classes.query.MetadataQuery(distance=True),
        distance=2.0  # Increase distance threshold to include more results
    )
    
    results = []
    for obj in response.objects:
        results.append({
            "content": obj.properties["content"][:500] + "..." if len(obj.properties["content"]) > 500 else obj.properties["content"],
            "source": obj.properties["source"],
            "chunk_index": obj.properties["chunk_index"],
            "distance": obj.metadata.distance
        })
    
    return results

def fetch_chunk_by_index(source_file: str, chunk_index: int, client: weaviate.WeaviateClient) -> Dict:
    """Fetch a specific chunk by source file and chunk index"""
    collection = client.collections.get(COLLECTION_NAME)
    
    response = collection.query.fetch_objects(
        filters=weaviate.classes.query.Filter.by_property("source").equal(source_file) & 
              weaviate.classes.query.Filter.by_property("chunk_index").equal(chunk_index),
        limit=1
    )
    
    if response.objects:
        obj = response.objects[0]
        return {
            "content": obj.properties["content"],
            "source": obj.properties["source"],
            "chunk_index": obj.properties["chunk_index"],
            "uuid": str(obj.uuid)
        }
    else:
        return None

def fetch_all_chunks_from_source(source_file: str, client: weaviate.WeaviateClient) -> List[Dict]:
    """Fetch all chunks from a specific source file, ordered by chunk_index"""
    collection = client.collections.get(COLLECTION_NAME)
    
    response = collection.query.fetch_objects(
        where=weaviate.classes.query.Filter.by_property("source").equal(source_file),
        limit=1000,  # Adjust based on expected number of chunks
        sort=weaviate.classes.query.Sort.by_property("chunk_index")
    )
    
    results = []
    for obj in response.objects:
        results.append({
            "content": obj.properties["content"],
            "source": obj.properties["source"],
            "chunk_index": obj.properties["chunk_index"],
            "uuid": str(obj.uuid)
        })
    
    return results

def fetch_chunks_range(source_file: str, start_index: int, end_index: int, client: weaviate.WeaviateClient) -> List[Dict]:
    """Fetch a range of chunks from a specific source file"""
    collection = client.collections.get(COLLECTION_NAME)
    
    response = collection.query.fetch_objects(
        where=weaviate.classes.query.Filter.by_property("source").equal(source_file) & 
              weaviate.classes.query.Filter.by_property("chunk_index").greater_or_equal(start_index) &
              weaviate.classes.query.Filter.by_property("chunk_index").less_or_equal(end_index),
        limit=1000,
        sort=weaviate.classes.query.Sort.by_property("chunk_index")
    )
    
    results = []
    for obj in response.objects:
        results.append({
            "content": obj.properties["content"],
            "source": obj.properties["source"],
            "chunk_index": obj.properties["chunk_index"],
            "uuid": str(obj.uuid)
        })
    
    return results

def main():
    """Example usage"""
    client = weaviate.connect_to_local(
        host="localhost", 
        port=8081,
        grpc_port=50051,
    )
    
    try:
        setup_weaviate_collection(client)
        
        # Example: Load PDF (uncomment and modify path as needed)
        pdf_path = Path.home() / os.getenv('FILE_PATH_RELATIVE_TO_HOME')
        # load_pdf_to_weaviate(pdf_path, client)
        
        labels = []
        ONTOLOGY_FILE = "biz-strategy-knowledge-base-ai/001_information-extraction/semantics/bizrisk.ttl"
        graph = Graph()
        g = graph.parse(ONTOLOGY_FILE)
        for cat in g.subjects(RDF.type, OWL.Class):  
            label = get_local_part(cat)
            labels.append(label)
        
        print(f"Extracted labels from the ontology: {labels}")
        # # query = str(labels)
        # query = "risks"
        # results = search_weaviate(query, client, limit=3)
        
        # print(f"\nSearch results")
        # for i, result in enumerate(results, 1):
        #     print(f"\n{i}. Distance: {result['distance']:.4f}")
        #     print(f"Source: {result['source']} (chunk {result['chunk_index']})")
        #     print(f"Content: {result['content']}")

        chunk_index = 76
        specific_chunk = fetch_chunk_by_index(str(pdf_path), chunk_index, client)
        if specific_chunk:
            print(f"\n1. Fetched chunk {chunk_index} from source:")
            print(f"   Content: {specific_chunk['content'][:200]}...")
        
        
    finally:
        client.close()

if __name__ == "__main__":
    main()
