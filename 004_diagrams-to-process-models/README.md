
How to model steps in Cypher?
- if multiple relationships, how to prioritize them?
- example of Plant UML: https://real-world-plantuml.com/umls/4613222493585408

How to traverse and get context?

PlantUML
- to ontology: https://github.com/GovDataOfficial/plantuml-to-ontology/
- or JSON?
- and then to Cypher? directly to Cypher?

Problem: no good model found for conversion to cypher from PlantUML
- Train on H2O LLM studio on 10k rows
- or on xet on hugging face: https://huggingface.co/datasets/neo4j/text2cypher-2025v1/viewer/default/train?p=2&views%5B%5D=train&row=200`
- maybe try with prodigy: https://prodi.gy/
- use synthetic data

# Collecting cases

**Taxonomy**

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

ignore sprites

make sure that relationships make sense.
- package refers groups components
- ...