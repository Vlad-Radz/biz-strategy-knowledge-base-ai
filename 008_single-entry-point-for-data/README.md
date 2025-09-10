
# Designing a Single Entry Point for Data with GraphQL, Knowledge Graphs and Ontologies

Organizations increasingly need a single, consistent entry point for accessing data spread across databases, data lakes, and services. GraphQL, combined with ontology-driven domain modeling, offers a powerful way to achieve this.


## Step 1: Build Relationships between scattered data

Most organizations face the challenge of scattered data assets—databases, catalogs, systems, and services that exist in silos. GraphQL provides a natural entry point for building relationships across these assets. Its schema-driven approach allows teams to define entities and their attributes, then connect them through a flexible API layer. This makes it possible to unify how data is queried and exposed, even if it remains distributed in heterogeneous backends.

### GraphQL as a Unified API Layer

GraphQL is not a database query language but an API query language that allows clients to specify exactly what data they need. It defines entities and their attributes (**types** and **fields**) as well as relationships between them, forming a data graph. Operations in GraphQL—queries, mutations, and subscriptions—are fulfilled by resolvers, which connect the API to underlying data stores.

Many database providers supply GraphQL libraries that convert GraphQL operations into queries against their native backends. However, when working with traditional relational stores, these libraries often require significant transformation and relationship mapping. This can result in duplicated data, awkward table structures, and technical debt. **Graph databases** alleviate much of this complexity because GraphQL type definitions naturally align with a graph-based data model, enforcing a strict type system while preserving relationships.

### Bridging Data Lakes and Real-Time Applications with GraphQL

A frequent challenge arises when making large data products available to thinner clients in real time. While columnar formats such as Parquet or ORC, along with in-memory formats like Apache Arrow, are highly efficient for analytics, they are not straightforward to expose through low-latency APIs. Tools like DataFusion help query Arrow data in memory, but serving this through GraphQL requires an additional layer.

The typical implementation involves exposing a GraphQL endpoint over data lake tables, generating a schema, and implementing resolvers that query pre-aggregated or optimized subsets of data. This allows internal microservices or applications to retrieve real-time statistics from Spark-generated datasets without direct access to raw files.

### AWS as an Example Implementation

On AWS, AppSync provides a managed GraphQL service that can unify access to multiple backends, including databases, microservices, and data lakes. Combined with Lake Formation and Glue Data Catalog, administrators can enforce fine-grained governance and control access at the table, column, or even cell level. Queries can be executed via Athena, triggered by Lambda functions orchestrated through AppSync, ensuring secure and performant access to S3-based data lakes.

This architecture supports multi-tenancy search, cataloging, and federation of data assets across organizational boundaries. Integration with AWS DataZone and Master Data Management services enables automated discovery, schema evolution, and governance enforcement, making it easier to define relationships for data mesh–based search and catalogs.


## Step 2: Moving Beyond Access: Studying Relationships in a Graph Database

If the goal is not just to access but to study and analyze relationships between data assets, a graph database becomes essential. Graph databases store connections natively, allowing for richer relationship modeling than traditional relational or document-based systems. These relationships can be explored using a proprietary query language like Cypher or expressed through GraphQL queries for broader developer adoption.

To power this, metadata must first be loaded into the graph. By representing metadata as graph nodes and edges—what we can call metadata types—we can create a [Meta Grid](https://olesenbagneux.medium.com/the-meta-grid-is-the-third-wave-of-data-decentralization-b18827711cec): a unifying knowledge graph that connects diverse metadata repositories.

The Four Types of Metadata

A metadata repository is most effective when it captures all four key types of metadata:
1. Descriptive – Labels, classifications, and other attributes that describe what the content is.
2. Structural – Information on how the data is organized, such as columns, formats, and data types.
3. Administrative – Management-related information, including access control, compliance policies, and audit trails like last-modified timestamps.
4. Semantic – Metadata that encodes relationships and meaning, enabling inference and contextual understanding.

Together, these types provide not just a catalog of data assets but a knowledge structure that connects IT, data, information, and knowledge management domains.

**Use Cases Enabled by Metadata knowledge graphs**. Building a metadata knowledge graph (as possible implementation of the ) unlocks a range of critical enterprise use cases:
- Lineage: Tracing how data flows across systems, transformations, and processes.
- Change management: Assessing the impact of schema changes, migrations, or policy updates across dependent assets.
- Discovery and search: Enabling richer queries across scattered metadata repositories.
- Governance and compliance: Embedding access rules and audit information within the graph itself.


## Step 3: Semantic Metadata and Ontologies

An especially powerful enabler is semantic metadata, which allows us to infer relationships and context. Ontologies describe concepts, relationships, and constraints, serving multiple roles:
- Helping data modelers, developers and other roles align on a shared vocabulary.
- Powering annotations and labeling of assets.
- serve as single source of truth for knowledge for both humans and machines.

### Unified Data Achitecture by Netflix

Ontologies can describe not only data, but also data sources / data containers themselves, ensuring interoperability.

Netflix has demonstrated this by using ontologies to define domain concepts and transpile them into GraphQL schemas and other data containers, effectively creating a single entry point for data. By aligning RDF URIs with GraphQL types, the ontology becomes executable and operational, not just descriptive.

```xml
type ONEPIECE_Character @key(fields: "onepiece_rname") @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#Character") {
  """
  The name of the entity in English.
  """
  onepiece_ename: String @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#ename")
  """
  A Devil Fruit that was consumed by the entity.
  """
  onepiece_devilFruit: ONEPIECE_DevilFruit @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#devilFruit")
  """
  The romanized name of the entity.
  """
  onepiece_rname: String! @udaUri(uri: "https://rdf.netflix.net/onto/onepiece#rname")
}
```
Source: [link](https://github.com/Netflix-Skunkworks/uda/blob/9627a97fcd972a41ec910be3f928ea7692d38714/uda-intro-blog/onepiece.graphqls)

Their Unified Data Architecture (UDA) enables teams to model a domain once and represent it across multiple systems, powering automation, discoverability, and semantic interoperability. Domain models can be transpiled into GraphQL schemas, making them accessible through GraphQL resolvers or domain graph services.

Unlike classical ontology frameworks, GraphQL introduces federation, modularity, and team ownership into the schema design process. **Global identifiers** - often encoded as opaque base64 strings - allow entities to be referenced consistently across systems, with resolvers handling the mapping back to local keys. Moreover, RDF-style URIs can be used to connect GraphQL types with semantic models, linking schema definitions to ontological knowledge.
