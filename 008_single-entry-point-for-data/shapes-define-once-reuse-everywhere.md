
SHACL (Shapes Constraint Language) is a constraint language for RDF graphs, allowing you to define and validate the structure and content of data (e.g., ensuring a property has a specific datatype or cardinality). You can use LLM models to generate SHACL shapes from your ontology, and then use these shapes in many different scenarios; with the help of SHACL you can make your objects self-sufficient.

Use cases:

1. most obvious: validating data before adding it to the graph.

2. add visual representation of your objects:

While SHACL primarily validates and describes RDF graph structures, there are approaches and tools that convert RDF data and SHACL shapes into visual representations or images for better comprehension. The shapes from the ontology should contain enough information to help the user interface builder select suitable input widgets.

DataShapes (DASH) helps render RDF data in web applications primarily by extending SHACL (Shapes Constraint Language) with additional vocabulary and conventions to define how RDF data should be presented and edited in user interfaces. DASH provides a set of reusable constraints, viewer/editor hints, and guidelines for generating user input forms and display layouts that mirror the RDF data model described by SHACL shapes.

Dash Widgets allow to identify how a particular property may get displayed. There are Editor components and Viewer components, corresponding to read-write and read-only components.

How DASH assists rendering RDF data:
- DASH builds on SHACL shapes which already define data constraints and validation rules. Beyond validation, SHACL includes terms like sh:order and sh:group for UI layout hints.
- DASH adds a vocabulary for specifying display and editor widgets (e.g., dash:viewer, dash:editor) tailored for RDF values such as IRIs or literal strings, which can be used by form builders and editors to render user-friendly RDF data input controls.
- DASH promotes standardization for form generation and user interface behaviors for RDF data, allowing tools to interpret shape definitions into dynamic, interactive forms for data entry or editing.
- It specifies how to handle multiple values, layout sections, data types, and constraints, enabling more natural RDF forms beyond basic validation.
- Tools can use DASH-enhanced SHACL shapes to automatically generate user interfaces that respect the data model both in presentation and validation.

Tools and Browser Support:
- By default, browsers do not natively render RDF data formatted with DASH directly as web forms or UIs.
- To utilize DASH, you need software or libraries that understand SHACL and DASH vocabularies and can convert shapes into HTML forms or RDF viewers. Examples include RDF shape editors or SHACL-aware form generators like TopBraid or FAIR Data Point clients.

These tools interpret DASH instructions to produce editable or display widgets for RDF data on the web.

Sources:
- https://www.linkedin.com/pulse/ontology-modeling-shacl-defining-forms-instance-data-holger-knublauch-ann5f/
- https://ontologist.substack.com/p/shacl-for-user-interfaces

3. Render your objects in HTML:

HTML, as a markup language, inherently preserves the order of elements — a property that carries through to the Document Object Model (DOM). This means that the order of nodes in the DOM matters.

In contrast, RDF is fundamentally unordered: a set of triples without inherent sequence. However, RDF provides mechanisms to represent order when needed. The most common approaches are RDF Collections (which use linked-list structures) and RDF Containers (which may use numbered predicates like rdf:_1, rdf:_2, etc.). Neither is ideal, but both make it possible to model ordered data.

A sequence represented as a linked list (an RDF Collection) is expressed in Turtle syntax as a space-separated list of items enclosed in parentheses:

```turtle
ex:Items ex:hasList (ex:Item1 ex:Item2 ex:Item3) .
```
[This article](https://ontologist.substack.com/p/rdf-as-document-language) describes well how to use this mechanism to render RDF objects in HTML.


4. validation for human prompts:

Based on the SHACL shapes, we can get an informal (free-text) or a formal SHACL validation report for validity of assertions in the prompt. [This article](https://open.substack.com/pub/ontologist/p/making-pizza-with-ai-and-shacl) describes it well.


5. diagram generator:

E.g. generate a mermaid file which represents what is possible to do with our object, from SHACL shapes. Inspired by [This article](https://open.substack.com/pub/ontologist/p/making-pizza-with-ai-and-shacl) describes it well.