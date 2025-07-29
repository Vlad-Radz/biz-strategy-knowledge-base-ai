# Prompt for an AI assitant

I want to showcase how ontologies can help with:
1. data interoperability: when diff. departments speak common language and can "translate" from own language to the language of other departments. --> this requires e.g. a layer of semantic master data.
2. asset management: when you use terms from an ontology or taxonomy to tag you assets like servers, databases and cloud resources.

My strategy:
- define classes like Company, Project, Product, Program, Portfolio, Operations - whatever fits
- demonstrate that diff. kinds of organisational initiatives listed above can have diff. governance or reporting policies, or structures.
- Introduce a class called somehow like ScopedResourcesExternalService, which can be an AWS Organisation, an AWS account, a Jira project, a Github repo etc.
- And the examples of RDF data that instantiate these classes, so that at the end I can execute queries to get information of what organisational unit type (project or program or something else) does an external resources represent. It can be important to know in order to correctly aggregate costs or apply governance policies.

Implementation steps for you:
1. Define organisational unit types that make sense for my use case. You can use a framework like Enterprise Architecture or something else.
2. Create an ontology: classes that you chose + the ScopedResourcesExternalService class (naming is up to you) + relationship to every of the classes that you chose.
3. Create multiple RDF instances for the ScopedResourcesExternalService (or whatever name would be) class, for diff. 3rd party services (like AWS, Jira, Github) and aggreation level (e.g. AWS Organisation vs. AWS Account). For each instance pick an instance of a organisational unit from the ontology, and create relationship that would bind them.
4. Create a query in SPARQL that would look for a class representing organisation unit that is related to the picked external service instance.
5. Describe how to use the classes from point 2 to tag resources in e.g. AWS (to implement ownership)
6. Create a query in cloudquery that would filter resources from AWS that belong to one of the classes from point 2.