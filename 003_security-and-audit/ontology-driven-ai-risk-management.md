# Ontologies as foundation for implementation of policies

## Overview

📝 This showcase demonstrates how ontologies enforce corporate security policies in the context of AI through executable code. We implement the [VAIR ontology](https://delaramglp.github.io/vair/) concepts as Python classes with automated compliance checking.

**Use Case Flow:**
1. Simple LLM wrapper with Pydantic AI + Ollama  
2. Risk controls implementing VAIR concepts (LoggingMeasure, MonitoringMeasure) + risk mitigation mapping
3. Compliance validation

💡 The following models can also be used to enhance the definition of AI risks:
- AI risk ontology: [AIRO](https://delaramglp.github.io/airo/) (VAIR is based on this one);
- The European Telecommunications Standards Institute (ETSI) [AI Threat Ontology](https://www.etsi.org/deliver/etsi_gr/SAI/001_099/001/01.01.01_60/gr_SAI001v010101p.pdf).

⚠️ **Note: the code snippets used here were not checked against a real-life scenario and are here merely for demonstration purposed**. They might contain bugs.

## 1. Simple LLM Wrapper with Pydantic AI

Let's imagine that we have a minimalistic LLM-based application.

`llm_wrapper.py`:
```python
from pydantic_ai import Agent
from pydantic import BaseModel

class AIResponse(BaseModel):
    content: str
    confidence: float

# Simple LLM wrapper using Ollama
agent = Agent("ollama:llama3.1", result_type=AIResponse)

async def query_llm(prompt: str) -> AIResponse:
    return await agent.run(prompt)
```

In the context of the security, we would certainly like that developers of the apps in out enterprise implement some guardrails which would check the response of the LLM models or least document them - e.g. in the form of logs or metrics. Our AI risk ontology describes various measures of controlling AI risks, and we want to make sure that developers implement them; we also would like to be able to monitor their implementation.

## 2. VAIR Ontology Implementation

Let's create functionality that would allows us to link Python objects to specific concepts from an ontology. In our case, that would mean that specific Python classes are referring to specific AI risks and mitigation measures from our ontology.

### Ontology Integration Approach

`ontology_integration.py`:
```python
from owlready2 import get_ontology

# Load VAIR ontology
vair_onto = get_ontology("file://./semantics/vair.ttl").load()

class OntologyMixin:
    """Links Python classes to VAIR ontology concepts."""
    
    @classmethod
    def ontology_class(cls):
        return getattr(vair_onto, cls.__name__, None)
    
    @classmethod
    def validate_ontology_compliance(cls) -> Dict[str, Any]:
        onto_class = cls.ontology_class()
        return {
            "class_name": cls.__name__,
            "ontology_bound": onto_class is not None,
            "ontology_uri": str(onto_class) if onto_class else None
        }

# Risk mitigation decorator
def mitigates_risk(risk_source: str):
    """
    a decorator that links a class to a specific ontological concept
    """
    def decorator(cls):
        if not hasattr(cls, '_mitigates_risks'):
            cls._mitigates_risks = []
        cls._mitigates_risks.append(risk_source)
        return cls
    return decorator
```

### Risk Control Implementations

Now that we have a mechanism of linking classes to ontological concepts, let's instantiate some specific risk mitigation measures.

`risk_controls.py`:
```python
import logging

@mitigates_risk("InaccurateDecision")
class LoggingMeasure(OntologyMixin):
    """
    Implements a concept from the ontology:
        vair:LoggingMeasure - for audit logging.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ai_risk_audit")
        self.logger.setLevel(logging.INFO)
    
    def log_interaction(self, prompt: str, response: str, employee_id: str):
        self.logger.info(f"Employee {employee_id}: {prompt[:50]}... -> {response[:50]}...")

@mitigates_risk("InaccurateDecision")
class MonitoringMeasure(OntologyMixin):
    """Implements vair:MonitoringMeasure - real-time monitoring."""
    
    def __init__(self):
        self.risk_threshold = 0.7
    
    def monitor_confidence(self, confidence: float) -> bool:
        """Returns True if confidence is below risk threshold."""
        return confidence < self.risk_threshold

@mitigates_risk("DataPoisoning")
@mitigates_risk("InputDataRiskSource") 
class InputValidator(OntologyMixin):
    """Validates input for data poisoning."""
    
    def validate_input(self, prompt: str) -> bool:
        suspicious_patterns = ["<script>", "DROP TABLE", "rm -rf"]
        return not any(pattern in prompt for pattern in suspicious_patterns)
```

## 3. Compliance Checking

Now we need a mechanism that would allow us to track the usage of ontological concepts. In our case, that means tracking the implementation of guardrails in AI-based applications.

On the development side, it means defining the interface of the software package properly. In Python, we can specify the classes that implement mitigation measures against AI risks. Important: in our example, names of the classes should be equal to the names of concepts in the ontology.

`__init__.py`:
```python
__all__ = ["LoggingMeasure", "MonitoringMeasure", "InputValidator"]
```

On the control side, we need a mechanism that would automatically check the software packages for implementation of guardrails. This can be done, for example, in the CICD pipelines.

`compliance_checker.py`:
```python
import ast
from pathlib import Path
from typing import Set, Dict

class OntologyComplianceChecker:
    REQUIRED_CONTROLS = {"LoggingMeasure", "MonitoringMeasure", "InputValidator"}
    REQUIRED_RISK_SOURCES = {"DataPoisoning", "InaccurateDecision", "InputDataRiskSource"}
    
    def check_package(self, package_path: str) -> Dict:
        # check using e.g. the ast ("Abstract Syntax Tree") package
        ...
```

## Benefits

This approach transforms abstract corporate policies into concrete, testable code with automatic validation, thanks to the following measures:
- **Policy as Code**: VAIR ontology concepts become executable Python classes
- **Automated Compliance**: CI/CD validates required risk controls are implemented  


## Maintaining ontologies at scale: inductive approach

Let's imagine that an enterprise has developed an ontology of the most important business concepts. As I showed in the demo 002 (different folder of this repository), creation of such layer for semantic master data would enable multiple use case - e.g. reusage of these concepts across the enterprise and its activities.

A maintainer of this ontology would certainly be interested in getting feedback about the model. Real feedback can be get if usage of ontologies is analyzed.

First of all, if ontology is used by e.g. software developers, it is already a good sign, as it would probably require changing some habits and processes. Whether developers use and refer to ontological concepts, can be tested by checking the software packages - in Python, that would be possible thanks to `__init__` files and the `ast` library.

But what if we could not only learn whether developers use our ontology, but also how the use it? How do these classes look like? What kind of properties and relationships do they have? You could treat software code as data by creating graph structures out of it, as I wrote in my [article](https://medium.com/analysts-corner/treating-your-code-as-data-unlocks-potential-for-ai-powered-code-modernization-not-just-3fe9c1105be1) "Treating your code as data unlocks potential for AI-powered code modernization, and not only that". You could create such graph using the aforementioned `ast` library, load it into a graph database and apply graph analysis and visualisation techniques to learn about the structure of the code.

This form of inductive learning could help to maintain your ontology and e.g. add new concepts to it.