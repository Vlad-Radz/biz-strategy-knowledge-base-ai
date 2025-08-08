
import asyncio
from pathlib import Path

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

ONTOLOGY_FILE = "biz-strategy-knowledge-base-ai/001_information-extraction/semantics/bizrisk.ttl"
FILE_TO_BE_PROCESSED = Path.home() / "Downloads" / "hexagon-202308010873-1.pdf"

NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "testtest"
###########################################

reader = PdfReader(FILE_TO_BE_PROCESSED)

text = ""
for page in reader.pages:
    text+=page.extract_text()   

# ############################

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

graph = Graph()
g = graph.parse(ONTOLOGY_FILE)

neo4j_schema = getSchemaFromOnto(g, ["Risk", "Organization"])
print(neo4j_schema)  # pydantic model -> Tuple of node types

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

asyncio.run(kg_builder.run_async(text=text))

for pk in getPKs(g):
    resolver = SinglePropertyExactMatchResolver(driver=driver, resolve_property=pk)
    asyncio.run(resolver.run())

driver.close()
