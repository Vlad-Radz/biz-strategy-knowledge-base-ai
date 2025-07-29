# AWS Resource Tagging Strategy Using Organizational Ontology

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

Create AWS Tag Policies that enforce ontology-based tagging:

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
        "Null": {
          "aws:RequestedRegion": "false"
        },
        "ForAnyValue:StringNotEquals": {
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

```sql
-- Cost by organizational unit type
SELECT 
    line_item_resource_id,
    resource_tags_user_unit_type as unit_type,
    resource_tags_user_unit_name as unit_name,
    resource_tags_user_cost_center as cost_center,
    SUM(line_item_unblended_cost) as total_cost
FROM cost_and_usage_report
WHERE month = '2025-01'
    AND resource_tags_user_unit_type IS NOT NULL
GROUP BY 1,2,3,4
ORDER BY total_cost DESC;

-- Cost by access level classification
SELECT 
    resource_tags_user_access_level as access_level,
    COUNT(DISTINCT line_item_resource_id) as resource_count,
    SUM(line_item_unblended_cost) as total_cost
FROM cost_and_usage_report
WHERE month = '2025-01'
    AND resource_tags_user_access_level IS NOT NULL
GROUP BY 1
ORDER BY total_cost DESC;
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
