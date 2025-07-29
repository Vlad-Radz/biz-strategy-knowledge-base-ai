# AWS Resource Tagging Strategy Using Organizational Ontology

⚠️ **Note: the information and queries used here were not checked against a real-life scenario and are here merely for demonstration purposed**

## Overview

This document describes how to implement a semantic tagging strategy for AWS resources based on the organizational ontology. This approach enables automated cost allocation, governance policy enforcement, and resource ownership tracking.

## Core Tagging Principles

### 1. Ontology-Driven Tags

All AWS resources should be tagged using standardized values derived from the organizational ontology:

- **org:OrganizationId**: Unique identifier from the ontology
- **org:UnitType**: Type of organizational unit (Project, Product, Department, etc.)
- **org:CostCenter**: Financial tracking code
- **org:BudgetCode**: Budget allocation code
- **org:AccessLevel**: Security classification
- **org:GovernancePolicy**: Applicable governance framework

### 2. Mandatory Tags

Every AWS resource must include these minimum tags:

```json
{
  "OrganizationId": "PROJ-ECP-001",
  "UnitType": "Project", 
  "UnitName": "E-Commerce Platform Replatform Project",
  "CostCenter": "CC-ECP-001",
  "BudgetCode": "BG-ECP-2025",
  "AccessLevel": "Restricted",
  "Environment": "Production|Staging|Development|Test",
  "Owner": "project.lead@techcorp.com",
  "ManagedBy": "DevOps Team"
}
```

### 3. Optional Enhancement Tags

Additional tags for enriched metadata:

```json
{
  "GovernancePolicy": "Project Management Standard",
  "ParentUnit": "PROG-CM-001",
  "ParentUnitType": "Program",
  "ServiceProvider": "AWS",
  "ScopeIdentifier": "123456789013",
  "DataClassification": "Confidential|Internal|Public",
  "BackupPolicy": "Daily|Weekly|Monthly|None",
  "MonitoringLevel": "Standard|Enhanced|Custom"
}
```

## Tag Policy Implementation

Create AWS SCP Policies that enforce ontology-based tagging (_if a user attempts to create EC2, RDS, or S3 resources without a OrganizationId tag matching the listed prefixes, the request is denied_):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RequireOrganizationalTags",
      "Effect": "Deny",
      "Action": [
        "ec2:RunInstances",
        "rds:CreateDBInstance",
        "s3:CreateBucket"
      ],
      "Resource": "*",
      "Condition": {
        "ForAnyValue:StringNotLike": {
          "aws:RequestTag/OrganizationId": [
            "PROJ-*",
            "PROD-*",
            "DEPT-*",
            "TEAM-*",
            "OPS-*"
          ]
        }
      }
    }
  ]
}
```


## Governance and Compliance

Create Config rules to ensure compliance with ontology-based tagging:

```json
{
  "ConfigRuleName": "required-organizational-tags",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "REQUIRED_TAGS"
  },
  "InputParameters": {
    "requiredTagKeys": "OrganizationId,UnitType,CostCenter,BudgetCode"
  },
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance",
      "AWS::RDS::DBInstance", 
      "AWS::S3::Bucket"
    ]
  }
}
```

This JSON config would be used in AWS Config, which:
- Continuously monitors AWS resources.
- Evaluates them against rules (like required tags).
- Flags noncompliant resources — but doesn’t stop them from being created.