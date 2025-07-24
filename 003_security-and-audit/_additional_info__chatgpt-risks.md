# AgentFlayer Attack Analysis - DPV AI Risks Ontology Coverage

This document describes an example of how the [Risk-AI ontology](https://github.com/w3c/dpv/blob/master/2.1/ai/ai-owl.ttl) can be used to model a new type of attack.

## Executive summary

The [AgentFlayer attack](https://www.linkedin.com/news/story/chatgpt-flaw-can-expose-data-7578202) represents a novel threat vector combining prompt injection with connector vulnerabilities. The current DPV AI Risks ontology lacks coverage for this attack class, requiring  new fundamental `SecurityAttack` types.

## Attack Description

*A vulnerability has been discovered in OpenAI - it concerns nuances in Connectors, which allows connecting ChatGPT to other services. "One infected document can leak 'secret' data through ChatGPT," say security researchers Michael Bargury and Tamira Ishaya Sharbat in their report. It is stated that it was the "weakness" in OpenAI's connectors that allowed the extraction of confidential information from a Google Drive account using an indirect prompt injection attack. In a demonstration of the attack, dubbed AgentFlayer, Bargury shows how a developer's secrets, in the form of API keys, stored in a demo Drive account, could be extracted. By the way, data can supposedly be extracted from Google Drive without any user interaction, experts add.*

## Ontology Coverage Analysis

### Current Security Attack Types in DPV AI Risks Ontology

The ontology (`001_information-extraction\semantics\risk-ai-owl.ttl`) currently includes these `SecurityAttack` subclasses:
- `AdversarialAttack`: "Inputs designed to cause the model to make a mistake"
- `DataPoisoning`: "Attack trying to manipulate the training dataset"
- `ModelEvasion`: "An input which seems normal for a human but is wrongly classified by ML models"
- `ModelInversion`: "Access to a model is abused to infer information about the training data"

### Coverage Gap Identified

**The AgentFlayer attack is covered by existing ontology classes.**
The Prompt injection attacks might be generally covered by `AdversarialAttack` type (as they make the model think that they execute a valid instruction).

At the same time, the Connector/integration-based vulnerabilities (leading to indirect data exfiltration through AI system connectors)  do something more sophisticated than just letting the model misclassify the content. This new type of attack executes an intrusion into the environment of AI-powered software ("agents") and injects a prompt indirectly.

So you might want to add new types to your ontology, such as e.g. `EnvironmentIntrusionAttack` or `IndirectPromptInjection`, if the existing classes are not sufficient for you.

```turtle
ai-owl:IndirectPromptInjection a rdfs:Class,
        owl:Class,
        dpv-owl:RiskConcept,
        risk-owl:IntegrityConcept,
        risk-owl:ConfidentialityConcept,
        risk-owl:PotentialConsequence,
        risk-owl:PotentialRisk,
        risk-owl:PotentialRiskSource ;
    dct:created "2024-12-01"^^xsd:date ;
    rdfs:isDefinedBy ai-owl: ;
    rdfs:subClassOf ai-owl:AdversarialAttack ;
    sw:term_status "accepted"@en ;
    skos:definition "Prompt injection attacks delivered through external data sources accessed by the AI system rather than direct user input"@en ;
    skos:prefLabel "Indirect Prompt Injection"@en ;
    skos:scopeNote "Malicious instructions embedded in documents, websites, or other external content that the AI system processes"@en .
```
