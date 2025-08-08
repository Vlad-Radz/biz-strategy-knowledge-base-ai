from rdflib.namespace import RDF, OWL, RDFS
from neo4j_graphrag.experimental.components.schema import (
    SchemaBuilder,
    NodeType,
    PropertyType,
    RelationshipType,
)

def getLocalPart(uri):
  """
  Get only class name by cutting off prefixes. Examples:
  1. http://example.com/ontology#FinancialRisk
  2. https://schema.org/Organization
  3. https://w3id.org/dpv:Risk
  """
  pos = -1
  pos = uri.rfind('#') 
  if pos < 0 :
    pos = uri.rfind('/')  
  if pos < 0 :
    pos = uri.rindex(':')
  return uri[pos+1:]



def getNLOntology(g):
  result = ''
  definedcats = []

  result += '\nNode Labels:\n'
  for cat in g.subjects(RDF.type, OWL.Class):  
    result += getLocalPart(cat)
    definedcats.append(cat)
    for desc in g.objects(cat,RDFS.comment):
        result += ': ' + desc + '\n'
  extracats = {}
  for cat in g.objects(None,RDFS.domain):
     if not cat in definedcats:
        extracats[cat] = None
  for cat in g.objects(None,RDFS.range):
     if not (cat.startswith("http://www.w3.org/2001/XMLSchema#") or cat in definedcats):
        extracats[cat] = None   
  
  for xtracat in extracats.keys():
     result += getLocalPart(xtracat) + ":\n"

  result += '\nNode Properties:\n'
  for att in g.subjects(RDF.type, OWL.DatatypeProperty):  
    result += getLocalPart(att)
    for dom in g.objects(att,RDFS.domain):
        result += ': Attribute that applies to entities of type ' + getLocalPart(dom)  
    for desc in g.objects(att,RDFS.comment):
        result += '. It represents ' + desc + '\n'

  result += '\nRelationships:\n'
  for att in g.subjects(RDF.type, OWL.ObjectProperty):  
    result += getLocalPart(att)
    for dom in g.objects(att,RDFS.domain):
        result += ': Relationship that connects entities of type ' + getLocalPart(dom)
    for ran in g.objects(att,RDFS.range):
        result += ' to entities of type ' + getLocalPart(ran)
    for desc in g.objects(att,RDFS.comment):
        result += '. It represents ' + desc + '\n'
  return result



def getPropertiesForClass(g, cat):
  props = []
  for dtp in g.subjects(RDFS.domain,cat):  # get all properties that apply to this class
    if (dtp, RDF.type, OWL.DatatypeProperty) in g:  # only pick OWL.DatatypeProperty properties; OWL.ObjectProperty is handled separately
      propName = getLocalPart(dtp)
      propDesc = next(g.objects(dtp,RDFS.comment),"")  # can yield multiple values (RDF allows multiple), but we only want the first one
      props.append(PropertyType(name=propName, type="STRING", description=propDesc))
  return props

def getSchemaFromOnto(g, classes_to_exclude=None):
  schema_builder = SchemaBuilder()
  classes = {}
  entities =[]
  rels =[]
  triples = []
  
  # get all subjects, for which predicate is rdf:type and objects are the specified classes
  for cat in g.subjects(RDF.type, OWL.Class):  
    if getLocalPart(cat) in classes_to_exclude:
        continue
    classes[cat] = None
    label = getLocalPart(cat)  # only get the actual class name
    props = getPropertiesForClass(g, cat)  # get OWL.DatatypeProperty properties for this class, returned as PropertyType data type
    entities.append(NodeType(label=label, 
                 description=next(g.objects(cat,RDFS.comment),""),   # can yield multiple values (RDF allows multiple), but we only want the first one
                 properties=props))  # includes properties for this class

  # do the same for RDFS.domain classes (just in case we missed some before)
  for cat in g.objects(None, RDFS.domain):
     if not cat in classes.keys():
        if getLocalPart(cat) in classes_to_exclude:
            continue
        classes[cat] = None
        label = getLocalPart(cat)
        props = getPropertiesForClass(g, cat)
        entities.append(NodeType(label=label, 
                    description=next(g.objects(cat,RDFS.comment),""),
                    properties=props))
  
  # do the same for RDFS.range classes (just in case we missed some before)
  for cat in g.objects(None, RDFS.range):
     if not (cat.startswith("http://www.w3.org/2001/XMLSchema#") or cat in classes.keys()):
        if getLocalPart(cat) in classes_to_exclude:
            continue
        classes[cat] = None
        label = getLocalPart(cat)
        props = getPropertiesForClass(g, cat)
        entities.append(NodeType(label=label, 
                    description=next(g.objects(cat,RDFS.comment),""),
                    properties=props))   
  
  for op in g.subjects(RDF.type, OWL.ObjectProperty):  
    relname = getLocalPart(op)
    rels.append(RelationshipType(label=relname, 
                               properties = [],
                               description=next(g.objects(op,RDFS.comment), "")))
    
  for op in g.subjects(RDF.type, OWL.ObjectProperty):
    relname = getLocalPart(op)
    doms = []
    rans = []
    for dom in g.objects(op,RDFS.domain):
        if dom in classes.keys():
          doms.append(getLocalPart(dom))
    for ran in g.objects(op,RDFS.range):
        if ran in classes.keys():
          rans.append(getLocalPart(ran))
    for d in doms:
       for r in rans:
          triples.append((d,relname,r))
  
  return schema_builder.create_schema_model(node_types=entities, 
                   relationship_types=rels,
                   patterns=triples)


def getPKs(g):
  keys = []
  for k in g.subjects(RDF.type, OWL.InverseFunctionalProperty):  
    keys.append(getLocalPart(k))
  return keys