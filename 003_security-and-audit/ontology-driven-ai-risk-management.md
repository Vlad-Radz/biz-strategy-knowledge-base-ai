# Ontology-Driven AI Risk Management with Pydantic AI

## Overview

This showcase demonstrates how ontologies enforce corporate AI policies through executable code. We implement VAIR ontology concepts as Python classes with automated compliance checking.

**Use Case Flow:**
1. Simple LLM wrapper with Pydantic AI + Ollama  
2. Risk controls implementing VAIR concepts (LoggingMeasure, MonitoringMeasure)
3. Decorator-based risk mitigation mapping
4. CI/CD compliance validation

## 1. Simple LLM Wrapper with Pydantic AI

```python
# llm_wrapper.py
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

## 2. VAIR Ontology Implementation

### Ontology Integration Approach

```python
# ontology_integration.py
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
    def decorator(cls):
        if not hasattr(cls, '_mitigates_risks'):
            cls._mitigates_risks = []
        cls._mitigates_risks.append(risk_source)
        return cls
    return decorator
```

### Risk Control Implementations

```python
# risk_controls.py
import logging

@mitigates_risk("InaccurateDecision")
class LoggingMeasure(OntologyMixin):
    """Implements vair:LoggingMeasure - audit logging."""
    
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

## 3. Defining the interface

```python
# Package interface (__init__.py)
__all__ = ["LoggingMeasure", "MonitoringMeasure", "InputValidator"]
```

## 4. CI/CD Compliance Checking

```python
# compliance_checker.py
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
