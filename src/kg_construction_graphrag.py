"""
Problems with this approach:
1. Introduces relationships that are not in the ontology.
2. It doesn't understand the view (e.g. company called Hexagon - events have to be interpreted from their point of view).
3. It doesn't generalize from risks in the text to risks in the ontology. And it doesn't use my categories at all.
4. It doesn't know domain and range - they are not included in the schema!
5. Too many tokens used!

Problems specific to missing func in his functions:
1. Point 3: it doesn't read the taxonomy --> check the function
    - a diff. type?
2. required should be true, not false
3. Also reads not all properties!
---> understand his solutions, and try to use it.
-- also get rid of taxonomy now, fix the foundational schema first
-- maybe then a post-processing for the adding a property for each riskevent
-- or alternative: go through all riskevents and check their type, and create relationship to a specific risk

Points 1-3 can potentially be solved by specifying the prompt.
Point 1 can potentially be solved by adding SHACL shapes --> get reports evaluated by an AI agent, which can fix the data?
Point 3 can potentially be solved by adding the taxonomy analysis as a tool (e.g. a SPARQL query)

UPDATE:
- prompt:
    - clear view and goal: we need facts or expectations of facts. But not just statements about facts.
    - use terms precisely. If doesn't fit, skip it
- how to omit the lexical graph and only leave the domain one?
- write code for calling the taxonomy, and each Risk -> extract name -> fit into taxonomy -> generate new data and connect with other nodes + place old name as comment -> remove old node
- revisit other problems mentioned above
"""

import asyncio

from pypdf import PdfReader
from neo4j import GraphDatabase
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm.openai_llm import OpenAILLM
from neo4j_graphrag.experimental.components.resolver import SinglePropertyExactMatchResolver
from rdflib import Graph
from rdflib.namespace import RDF, SKOS

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
    # prompt_template="",
    from_pdf=False,
)

asyncio.run(kg_builder.run_async(text=text))

for pk in getPKs(g):
    resolver = SinglePropertyExactMatchResolver(driver=driver, resolve_property=pk)
    asyncio.run(resolver.run())

driver.close()
