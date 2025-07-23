
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

- Add :RiskTreatmentMethod, with possible categories: EliminateRisk, AvoidRisk, TransferRisk, ReduceRisk, RiskControl, ShareRisk, HaltSource, RemoveSource, RemoveImpact, RemoveConsequence, MonitorConsequence, MonitorImpact, MonitorRiskSource, etc.
- Distinguish between risk response and treatment / preparation strategy? Can be both at the same time.
- RiskEventCauses


## Other ontologies and taxonomies

for Consequences: look for risk-owl:PotentialConsequence in https://github.com/w3c/dpv/blob/master/2.1/risk/risk-owl.ttl

AI risk ontology: https://delaramglp.github.io/airo/

Great taxonomy: https://www.openriskmanual.org/wiki/NACE_2.1_Classification


-----------------------------------------------

# Data extraction process

3 options for architecture:
1.  use Jesus' github session29 to load ontology + write SHACL to control (if neosemantics works; you can see what violated the shapes) + session 30 to load pdf
2. if needed: agentic checks + serialize not in Cypher, but in RDF, or even better: JSON + pydantic validator (and LLM that supports output in certain format)
3. session 31: GraphRAG with schema (derived from ontology), entity resolution and Q&A (cypher construction based on onto)

- Будет экстрагировать только те классы, что надо
- Post-processing: N10s has a Cypher endpoint, which can convert results of Cypher query to RDF -> if you want to prepare data for semantic web tools


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
- Wardley
- reasoners
- XBRL + MCP
    - installation: https://sec-edgar-mcp.amorelli.tech/setup/installation
- expose MCP server like here for strategy planning? https://github.com/stefanoamorelli/sec-edgar-mcp/blob/main/sec_edgar_mcp/server.py
- process modeling
- Decompose EU AI Act
- Use graph data science to show strange processes



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