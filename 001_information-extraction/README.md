
# Ontology design

## Some choices

Why specify that both rdfs:Class and owl:Class?
- owl:Class signals you expect OWL reasoning capabilities (e.g., consistency checking, complex inferences).
- rdfs:Class signals basic RDF Schema class typing.
--> to support a broad range of clients.

Why SKOS and OWL:Class at the same time? Experiment: try to have best of both worlds: formal reasoning capabilities from OWL and vocabulary management from SKOS.

Why DOLCE, although I like BFO?
DOLCE rigorously treats mental objects as:
- Non-physical and non-social, in that they have no independent physical location or existence outside an agent’s mind.
- Specific to a single intentional agent: The same mental object cannot simultaneously depend on multiple agents.
- Fundamental to representing cognitive states, attitudes, and internal representations such as beliefs, desires, intentions, and percepts.
--- BFO: about science. Not good to model abstract things.
- Instead, DOLCE offered the concept of mental object: mental objects are classified as a subtype of non-physical objects that are specifically dependent on an intentional agent (such as a person or other agent capable of having mental states).These are distinct from social or physical objects and are considered “private” experiences or entities, in contrast to objects that exist independently in the external world
- I just started.

what is the "by" language?

I aggregated risks on the family level, as I wanted to keep the knowledge base concise.

## Ideas for improving the ontology:

- Add :RiskTreatmentMethod. Distinguish between risk response and treatment / preparation strategy? Can be both at the same time.
- RiskEventCauses


## Other ontologies and taxonomies

dpv:
- https://w3c.github.io/dpv/2.1/dpv/
- https://w3c.github.io/dpv/2.0/dpv/modules/risk.html
- https://github.com/w3c/dpv/blob/master/2.1/dpv/dpv-owl.ttl
- https://github.com/w3c/dpv/blob/master/2.1/risk/risk.ttl (SKOS)
- https://github.com/w3c/dpv/blob/master/2.1/risk/risk-owl.ttl (OWL)

for Consequences: look for risk-owl:PotentialConsequence in https://github.com/w3c/dpv/blob/master/2.1/risk/risk-owl.ttl

AI risk ontology: https://delaramglp.github.io/airo/ and another one: https://www.linkedin.com/posts/razirais_etsi-artificial-intelligence-threat-ontology-activity-7355311015246381056-zmlf

Great taxonomy: https://www.openriskmanual.org/wiki/NACE_2.1_Classification

One more taxonomy of AI risks: https://www.linkedin.com/posts/pradeeps_ai-risk-mitigation-activity-7356172503834095616-CTqc


-----------------------------------------------

# Data extraction process

3 options for architecture:
1. load ontology + write SHACL to control (in neosemantics, you can see what violated the shapes)
2. serialize not in Cypher, but in RDF, or even better: JSON + pydantic validator (and LLM that supports output in certain format)
3. GraphRAG with schema (derived from ontology), entity resolution and Q&A (cypher construction based on onto)
--> I picked the third option.

3 options for processing of large documents:
1. Process pdf in chunks of 5 / 10 pages with GraphRAG. Problems: 1) disambuigation / deduplication? 2) The numeration of chunks in the graph - is there a way to keep the sequential numeration, or will it try to start with 1 every time?
2. Load lexical graph -> do RAG / similarity search based on specific ontology -> choose chunks that are relevant for the domain graph -> build the domain graph based on those chunks. That would be better for building a true metadata knowledge graph, and to allow enrichment of the KG with different views (expressed as ontologies), but I didn't need it for my personal, simple use case.
3. Do similarity search locally -> pick only relevant pieces of the document -> construct KG.
--> I picked the third option.

How to improve:
- Pre-processing: agentic checks
- Post-processing: N10s has a Cypher endpoint, which can convert results of Cypher query to RDF -> if you want to prepare data for semantic web tools
- Post-processing: SHACL



-----------------------------------------------


# Connection to Wardley maps

Goal: create situational awareness. E.g. KITS Eyecare can e.g. go to new markets; Redcare can merge with Docmorris.

We can build modularily —-> Wardley maps:

1. taxonomy of patterns -> create a lib -> link risks or financial situation to possible choices?
    - https://learnwardleymapping.com/leadership/
    - https://learnwardleymapping.com/climate/
2. Populate the wardley map of a company based on annual report, to: stage of evolution, futurecurrent stage of evolution, inertia, required actions e.g. strategic investment; chance and risk, business termobap the products of compan


cooperate, collaborate, conflict + border
constraint, strategic investment



# Future development

Future development:
- check alternatives to GraphRAG --> think of solution for generating libraries of knowledge. E.g. strategy patterns. Inductive patterns for ontology construction and maintenance.
- Wardley
- reasoners: subclass relationships, domain/range constraints, owl:sameAs, owl:inverseOf, disjoint classes, transitive properties, SWRL rules. Description logic inference: owl:intersectionOf, owl:unionOf, owl:someValuesFrom ——> use Apache Jena to infer data before loading to Neo4j.  
    - If you want to work with RDF triple and not Neo4j, then you don't necessarily need inference. Instead, you could put a lot of the (business) logic into the query rather than into the data model. SPARQL makes it possible to establish a context of operation in ways that inferencing does not. + use SHACL for validation.
- XBRL + MCP
    - installation: https://sec-edgar-mcp.amorelli.tech/setup/installation
- expose MCP server like here for strategy planning? https://github.com/stefanoamorelli/sec-edgar-mcp/blob/main/sec_edgar_mcp/server.py
- process modeling
- Decompose EU AI Act
- Use graph data science to show strange processes
- submit a data model for risk management? https://neo4j.com/developer/industry-use-cases/data-models/transactions/transactions-base-model/
- RDF preview extension: [link](https://github.com/LucienRbl/rdf-preview). Visualize VS code, structure



## modeling processes

2 ontologies: one for operational continuity, another for workflows (more dynamic one). --> Use BFO for both, extend it by classes OR use BPMN on Camunda.
- BPMN: it is to describe process for humans. No easy way to transform to RDF. It can be exposed, searched and queried in Camunda

Alternatives:
- UML in XML to OWL: link.
- Prov-O
- Gist as alternative to BFO: link. gistBFO is aligned with BFO.
- Alternative for BPMN: CMMN, for less structured workflows, more event-driven

CDRTO concepts:
- Control
- Data
- Resource
- Trace
- Online

BFO. Extend via e.g. CDRTO classes or these classes: [link](https://www.linkedin.com/feed/update/urn:li:activity:7331379118527160320)
- for things which have instances in space and time -> realism philosophy (allows to model things after scientific understanding, semantically correct)
- Principles of realism: all classes will have instances; differences between classes are reflecting joints (суставы) of reality; don’t use the word „concept“ to name things that exist in reality; child cannot be an ontology class as child is not a universal (is a temporary thing), but a dog is.
- BFO is like a legislation
- Can I use CLIF in Turtle? Precedes etc.? Or is it part of BFO? —-> yes and yes

Modeling of processes:
- events vs. state. Events: Look into OCEL: [link](https://www.ocel-standard.org/2.0/ocel20_specification.pdf)
- Processes vs subprocesses, CDRTO
- temporal relationships: sequential (precedes), overlap (contains, overlaps), distance (5 mins before), periodicity (every Thu); also causal, participation, hierarchical relationship

Alternatives to GraphRAG:
- https://github.com/AuvaLab/itext2kg
- https://github.com/LMMApplication/RAKG 