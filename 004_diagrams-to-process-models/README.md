# Constructing digital models of business processes from diagrams

*This demo is based on a real case from my work.*

**Scenario**: I am a programmer. I have a web app which provides an API endpoint where clients can pull certain data. At first they have to be able to authenticate. Authentication flow is handled by a proxy server in front of the web app and an IDP provider.

For some reason, a client cannot authenticate properly although it has a valid user. So what is the problem?
- maybe user does not enough permissions
- or a valid certificate
- or the endpoint doesn't work
- or user is not added to the web app at all
- or user exists and is added to the web app, but is not added to the environment and thus its certificate is not recognized
- or the client does not have the proper logic for certificate-based authentication

I want to make coding assistants smarter by feeding the process models them. My hypothesis is that if a coding assistants knows the IT infrastructure of the company, the way how networking is set up, how users can authenticated against endpoints, then it would be able to provide a more useful debugging tips.


# Theory

## Modeling frameworks

- 𝗕𝘂𝘀𝗶𝗻𝗲𝘀𝘀 𝗠𝗼𝗱𝗲𝗹𝗹𝗶𝗻𝗴 → roles, goals, outcomes
- 𝗣𝗿𝗼𝗰𝗲𝘀𝘀 𝗠𝗼𝗱𝗲𝗹𝗹𝗶𝗻𝗴 (𝗕𝗣𝗠) → steps, flows, handoffs
- 𝗕𝗣𝗠𝗡 → standardised visual grammar. Alternative for BPMN: CMMN, for less structured workflows, more event-driven
- 𝗗𝗼𝗺𝗮𝗶𝗻-𝗗𝗿𝗶𝘃𝗲𝗻 𝗗𝗲𝘀𝗶𝗴𝗻 (𝗗𝗗𝗗) → bounded contexts, ubiquitous language
- 𝗘𝗻𝘁𝗲𝗿𝗽𝗿𝗶𝘀𝗲 𝗗𝗮𝘁𝗮 𝗠𝗼𝗱𝗲𝗹𝗹𝗶𝗻𝗴 → interoperability and shared definitions
- 𝗖𝗼𝗻𝗰𝗲𝗽𝘁𝘂𝗮𝗹 / 𝗟𝗼𝗴𝗶𝗰𝗮𝗹 𝗔𝗿𝗰𝗵𝗶𝘁𝗲𝗰𝘁𝘂𝗿𝗲 → bridge from business vision to tech design

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

How to base on BFO?
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



## Converting from UML into Cypher

In my demo, I am working with PlanUML.
- it can be converted into an ontology (RDF): https://github.com/GovDataOfficial/plantuml-to-ontology/ --> check if fits to my case
- can it be converted to JSON?

Example of Plant UML: https://real-world-plantuml.com/umls/4613222493585408

How to model steps in Cypher?
- if multiple relationships, how to prioritize them?

--------------------------------------------

# Collecting cases

**Taxonomy** for PlantUML

Package can contain or refer to a component:
```bash
package "<$bitbucket{scale=0.3}> Bitbucket" as bitbucket {
    component "<$git-icon{scale=0.3}> eso" as gitEso {
    }
}
```

Actor, participant, database (as a separate class)
```bash
actor "DevOps /\nArgoCD (auto-sync)" as DevOps
participant "<$argo-icon{scale=0.3}> ArgoCD" as Argo
participant "<$openshift{scale=0.3}> Openshift" as K8s
database "Database" as Database
```

They can have relationships - will look like a sequence diagram:
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


# pre-Cypher schema

## Generate a schema first

```
Node properties:
- **<NodeName>**
    - `<property_name>`: <DATA_TYPE>
        - optional: Available options: [<comma-separated values>]
        - optional for integer and float values: Min: ..., Max: ...
        - optional: Example
Relationship properties:
- **<RELATIONSHIP>**
    - `propertyName`: <DATA_TYPE>
        - optional: Available options: [<comma-separated values>]
        - optional for integer and float values: Min: ..., Max: ...
        - optional: Example
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

## Then validate a schema

ignore sprites (a term from PlantUML)

make sure that relationships make sense.
- e.g. can a "package" have relationship to the "group" nodes?


# Ideas for the future

Problem: no good model found for conversion to cypher from PlantUML
- Train on a platform like H2O LLM studio on 10k rows
- or on `xet` on hugging face: https://huggingface.co/datasets/neo4j/text2cypher-2025v1/viewer/default/train?p=2&views%5B%5D=train&row=200`
- maybe try out prodigy for preparing data: https://prodi.gy/
- use synthetic data?

Fine-tune for such conversions based on model such as the [minimalistic](https://developers.googleblog.com/en/introducing-gemma-3-270m/) gemma 3 (270m).
