"""
Point 1 can potentially be solved by adding SHACL shapes --> get reports evaluated by an AI agent, which can fix the data?


UPDATE:
1. how to omit the lexical graph and only leave the domain one? --> write a Cypher query
2. write code for calling the taxonomy, and each Risk -> extract name -> fit into taxonomy -> generate new data and connect with other nodes + place old name as comment -> remove old node
3. think what to do with large PDFs. How chunks are currently handled? Use Weaviate?
4. spin up a vLLM container or fire up llama.cpp -> Qwen3-Coder, freshly baked, Apache2-licensed MoE, and small enough to run on my desk —> compare to other Qwens (e.g. DeepSeek-R1-0528-Qwen3-8B)
"""

import asyncio

from pypdf import PdfReader
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm.openai_llm import OpenAILLM
from neo4j_graphrag.experimental.components.resolver import SinglePropertyExactMatchResolver
# from neo4j_graphrag.generation.prompts import PromptTemplate
from rdflib import Graph

from utils import getSchemaFromOnto, getPKs

####### VARIABLES #########################

ONTOLOGY_FILE = "bizrisk.ttl"
FILE_TO_BE_PROCESSED = "C:/Users/UladzislauRadziuk/Downloads/hexagon-202308010873-1.pdf"

NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "testtest"

####### STEP1: GET THE UNSTRUCTURED CONTENT #########################

reader = PdfReader(FILE_TO_BE_PROCESSED)

text = ""
for page in reader.pages:
    text+=page.extract_text()   

# ############################

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

graph = Graph()
g = graph.parse(ONTOLOGY_FILE)

# for concept in g.subjects(RDF.type, SKOS.Concept):
#     print(f"SKOS Concept: {concept}")

neo4j_schema = getSchemaFromOnto(g)
print(neo4j_schema)  # pydantic model -> Tuple of node types

# prompt_template = PromptTemplate(
#     template='''
#     Your role:
#         - You are an information extraction expert. Called Json Statham.
#         - Use the proposed schema extract facts from the text.
#     Your methodology:
#         - Only extract facts that are relevant to the schema. Skip those which don't fit into the schema.
#         - Don't define new classes, properties or relationships. Given schema is complete.
#     Your view:
#         - the company that is main subject of the text that you will get.
#         - Extract information from the point of view of this company.
#     Warning:
#         - We rely on you extracting the information precisely.
#     Schema: {schema}
#     ''',
#     expected_inputs=['schema']
# )
# prompt = prompt_template.format(schema=neo4j_schema)

splitter = FixedSizeSplitter(chunk_size=2500, chunk_overlap=10)
embedder = OpenAIEmbeddings(model="text-embedding-3-small")

llm = OpenAILLM(
    model_name="gpt-4o",
    model_params={
        "max_tokens": 3000,
        "response_format": {"type": "json_object"},
        "temperature": 0,
    },
)

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

asyncio.run(kg_builder.run_async(text=text))

for pk in getPKs(g):
    resolver = SinglePropertyExactMatchResolver(driver=driver, resolve_property=pk)
    asyncio.run(resolver.run())

driver.close()
