# Constructing digital models of business processes from diagrams

*This demo is based on a real case from my work.*

**Scenario**: I am a programmer. I have a web app which provides an API endpoint where clients can pull certain data. At first they have to be able to authenticate. Authentication flow is handled by a proxy server in front of the web app and an IDP provider.

For some reason, a client cannot authenticate properly although it has a valid user. So what is the problem?
- maybe user does not enough permissions
- or a valid certificate to authenticate themselves
- or the API endpoint doesn't work
- or user is not registered at the web app at all
- or user exists and is registered at the web app, but is not added to the environment and thus its certificate is not recognized
- or the client does not have the proper logic for certificate-based authentication

I want to make coding assistants smarter by feeding the process models to them. My hypothesis is that if a coding assistant knows the IT infrastructure of the company, the way how networking is set up, how users can be authenticated against API endpoints, then it would be able to provide more useful debugging tips.


# Theory

## Modeling frameworks

Different modeling framework are used to represent different views on the system:

- Business modeling → roles, goals, outcomes
- Process modeling (BPM) → steps, flows, handoffs
- BPMN → standardised visual notation. Alternative for BPMN: CMMN, for less structured, more event-driven workflows.
- Domain-driven design (DDD) → domains represented via bounded contexts and ubiquitous language
- Enterprise Data Modeling → interoperability and shared definitions

## How to model processes with ontologies

Best practices is to have 2 ontologies:
1. one for operational continuity
2. another one - for workflows (more dynamic one).
--> Use foundational ontology like BFO for both, extend it by required classes; alternatively use other mature ontologies like Prov-O for foundation; alternatively use the Gist ontology (gistBFO is aligned with BFO).
--> use the BPMN notation to describe processes for humans. No easy way to transform to RDF. But it can be exposed, searched and queried in specialized tools like Camunda.

Another useful classification for building blocks of processes was presented in a [paper](https://drops.dagstuhl.de/entities/document/10.4230/TGDK.2.1.1) about CDRTO concepts:
- Control
- Data
- Resource
- Trace
- Online

How to base a domain ontology on BFO?
- Extend via e.g. CDRTO classes or [other](https://www.linkedin.com/feed/update/urn:li:activity:7331379118527160320) classifications of "archetypes".
- BFO is good for things which have instances in space and time -> realism philosophy (allows to model things after scientific understanding, semantically correct). Principles of realism:
    - all classes will have instances;
    - differences between classes are reflecting joints of reality
    - don’t use the word "concept" to name things that exist in reality
    - example: child cannot be an ontology class as child is not a universal (is a temporary thing), but a dog is.
- treat it like a legislation

Modeling of processes:
- distinguish events vs. state.
    - for modeling events: Look into OCEL: [link](https://www.ocel-standard.org/2.0/ocel20_specification.pdf)
- Processes vs subprocesses
- temporal relationships: sequential (precedes), overlap (contains, overlaps), distance (5 mins before), periodicity (every Thu); also causal, participation, hierarchical relationship


--------------------------------------------

## PlantUML notation

In my demo, I am working with `PlanUML`.
- it can be converted into an ontology (RDF): https://github.com/GovDataOfficial/plantuml-to-ontology/ --> check if fits to my case
- can UML be converted to JSON?

Example of Plant UML: https://real-world-plantuml.com/umls/4613222493585408


### **Taxonomy** for PlantUML

Package can contain or refer to a component:
```bash
package "<$bitbucket{scale=0.3}> Bitbucket" as bitbucket {
    component "<$git-icon{scale=0.3}> eso" as gitEso {
    }
}
```

Actor, participant, database (as separate classes)
```bash
actor "DevOps /\nArgoCD (auto-sync)" as DevOps
participant "<$argo-icon{scale=0.3}> ArgoCD" as Argo
participant "<$openshift{scale=0.3}> Openshift" as K8s
database "Database" as Database
```

Instances of those classes can have relationships and visualize as a sequence diagram:
```bash
DevOps -> Argo: Initiate Sync
```

Steps ("alt") can be grouped into a group:
```bash
group pre-install hooks
    == helm.sh/hook: pre-install\nhelm.sh/hook-weight: "-11" ==

    alt preJob.dbDrop.enabled == true
        Argo -> K8s: Scale web app deployment to 0
        note right
            Webb app should not run when deleting it's DB
        end note
    end alt

    alt preJob.pvcCleanup.enabled == true
        Argo -> K8s: Scale all deployments to 0
        note right
            PVCs can't be deleted, if those are still in use by any of the pods.
        end note
    end alt
```

----------------------

**Components**

Component can be named:
```bash
component "<$git-icon{scale=0.3}> webapp-deploy" as gitWebService {
    }
```

Component can connect to another component. Relationships can be directed and have a name. Length of arrow doesn't matter.

```bash
gitApplication -----> helmWebService : refers
helmWebService -> gitWebService : published from
```

Component can have a comment:

```bash
note left of "gitEso"
    Helm Chart of External Secrets Operator (ESO)
end note

note left of "gitApplication"
    ArgoCD GitOps repository:
    * central repository,
      where ArgoCD applications are defined
end note
```

--------------------

**Process modeling**

Steps ("alt") can be:
- grouped into a "group"
- have a title ("==")
- have a condition (after "alt")
- connect components (participants) ("Argo -> K8s")
- have a note ("note")

```bash
group pre-install hooks
    == helm.sh/hook: pre-install\nhelm.sh/hook-weight: "-11" ==

    alt preJob.dbDrop.enabled == true
        Argo -> K8s: Scale web app deployment to 0
        note right
            Webb app should not run when deleting it's DB
        end note
    end alt

    alt preJob.pvcCleanup.enabled == true
        Argo -> K8s: Scale all deployments to 0
        note right
            PVCs can't be deleted, if those are still in use by any of the pods.
        end note
    end alt
```

Model temporal sequences:
- activate: start a phase

```bash
!definelong Refresh()
    activate ArgoCD
        note right of ArgoCD
            Compare the latest code in Git with the live state.
            Figure out what is different.
        end note

        ArgoCD -> GitOps : Refresh
        activate GitOps
            return
        deactivate GitOps
        ArgoCD -> GitHelm : Refresh
        activate GitHelm
            return
        deactivate GitHelm
    deactivate ArgoCD
!enddefinelong

group Manual Worflow
    DevOps -> ArgoCD : Refresh
    Refresh()
end
```

-----------------------------

# Implementing a knowledge graph from UML


## Convert UML to Cypher

### Generate a schema first

Prompt:

```
**Context**:
I am a programmer. I have a web app for ALM (application lifecycle management) which provides an API endpoint where clients can pull certain data. But at first they have to be able to authenticate themselves.

**Your role**:
You are data extraction specialist.

**Your task**:
You have to process the PlantUML code and extract information from it according to a schema. Schema will be attached. Schema contains nodes and relationships between them. In this matter you have to connect real-world object instance from the PlantUML code in a meaningful way.

**Guidelines**:
- the source code for PlantUML defines a sequence diagram, so interpret vocabulary accordingly.
- Use the "note" property of nodes and relationships to add details in free-form.
- no detail shall be lost!
- You may extract only 1 (one) Process node! And relate all other extracted nodes to the Process node.
- Don't forget to connect nodes through relationships at the end.
- Schema contains nodes, relationships and properties whose names are put into "<>", which means that you are free to add new types for nodes, relationships and properties, but only where you are sure that it makes sense to introduce new types instead of using the free-form texts in the "note" property.
```

Format of a generic schema:
```
Node properties:
- **<NodeName>**
    - `<property_name>`: <DATA_TYPE>
        - optional: Available options: [<comma-separated values>]
        - optional for integer and float values: Min: ..., Max: ...
        - optional: Example
    - `NOTE`: STRING
        - Value: <free form text including some background details>
        - optional: Example
Relationship properties:
- **<RELATIONSHIP>**
    - `<propertyName>`: <DATA_TYPE>
        - optional: Available options: [<comma-separated values>]
        - optional for integer and float values: Min: ..., Max: ...
        - optional: Example
    - `NOTE`: STRING
        - Value: <free form text including some background details>
        - optional: Example
The relationships:
(:<NodeName>)-[:<RELATIONSHIP>]->(:<NodeName>)
```

Format of a task-specific schema:
```
- **Process**
    - `name`: STRING
    - `NOTE`: STRING
        - value: <free form text including some background details>
- **Component**
    - `name`: STRING
    - `type`: STRING
        - optional: ["security_component", "web app", "..."]
    - `NOTE`: STRING
        - value: <free form text including some background details>
- **User**
    - `id`: STRING
        - optional: value: <name or ID of the user>
    - `NOTE`: STRING
        - value: <free form text including some background details>
    - `<propertyName>`: <DATA_TYPE>
        - optional: Available options: [<comma-separated values>]
        - optional for integer and float values: Min: ..., Max: ...
        - optional: Example
Relationship properties:
- **SENDS_REQUEST_TO**
    - `NOTE`: STRING
        - value: <free form text including some background details>
    - `STEP`: INTEGER
        - value: <from processual point of view, number of this step in the sequence>
- **RESPONSES_TO**
    - `NOTE`: STRING
        - value: <free form text including some background details>
The relationships:
(:<NodeName>)-[:<RELATIONSHIP>]->(:<NodeName>)
```

Example:
- **DataCenter**
    - `name`: STRING Available options: ['DC1']
    - `location`: STRING Available options: ['Iceland, Rekjavik']
- **Rack**
    - `name`: STRING Example: "DC1-RCK-1-1"
    - `zone`: INTEGER Min: 1, Max: 4
    - `rack`: INTEGER Min: 1, Max: 10
- **Process**
    - `name`: STRING Example: "7.1"
    - `startTime`: INTEGER Example: "1605946409388"
    - `pid`: INTEGER Example: "8966"
- **Product**
    - `productName`: STRING Example: "Chai"
    - `discontinued`: BOOLEAN
    - `categoryID`: STRING Available options: ['1', '2', '7', '6', '8', '4', '3', '5']
    - `reorderLevel`: INTEGER Min: 0, Max: 30
    - `unitPrice`: FLOAT Min: 2.5, Max: 263.5

Relationship properties:
- **ORDERS**
    - `orderID: STRING` Example: "10248"
    - `unitPrice: STRING` Example: "34.80"
    - `productID: STRING` Example: "72"
    - `quantity: INTEGER` Min: 1, Max: 130
    - `discount: STRING` Example: "0"

The relationships:
(:DataCenter)-[:CONTAINS]->(:Rack)
(:Order)-[:ORDERS]->(:Product)

### Then validate a schema

Some validation rules:
- ignore sprites (a term from PlantUML)
- make sure that relationships make sense.
    - e.g. can a "package" have relationship to the "group" nodes?


### Then create Cypher from schema

---------------------------------------------------


## Modeling processes in KG based on UML

Modeling steps in Cypher:
- If multiple relationships of the same type between 2 nodes, how to make sure that traversal respects the right order?

## Traversing the graph

When I want to compare the logs to specific interactions between 2 nodes, to check if any specific interaction could plausibly cause an error from those logs, how do I do it best?
- collect all data I can, and then iterate through each relationship and estimate whether it could be the one that caused the error?
- or it is possible to "lazily" traverse, one by one?

## Adding more data points

This repo contains a diagram of the authentication flow. Additional data points could include:
- why the ALM tool has multiple URLs? Internal on OpenShift, external, etc.
- where the ALM tool is deployed and how does the networking setup look like?
- description of the process of registering users at IDP and assigning them to group so that they can get into specific namespaces and get access to the web app

-----------------------------------

# Ideas for the future

Problem: no good model found for conversion to cypher from PlantUML
- Train on a platform like H2O LLM studio on 10k rows
- or on `xet` on hugging face: https://huggingface.co/datasets/neo4j/text2cypher-2025v1/viewer/default/train?p=2&views%5B%5D=train&row=200`
- maybe try out prodigy for preparing data: https://prodi.gy/
- use synthetic data?

Fine-tune for such conversions based on model such as the [minimalistic](https://developers.googleblog.com/en/introducing-gemma-3-270m/) gemma 3 (270m).
