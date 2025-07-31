# CloudQuery Configuration for Organizational Unit Resource Filtering

⚠️ **Note: the information and queries used here were not checked against a real-life scenario and are here merely for demonstration purposed**. They might contain bugs.

## Overview

CloudQuery configurations to extract and filter AWS resources based on organizational ontology classifications. This enables resource discovery, cost analysis, and compliance reporting aligned with organizational structures.

## Base Configuration

### cloudquery.yaml

```yaml
kind: source
spec:
  name: "aws"
  path: "cloudquery/aws"
  version: "v25.0.0"
  destinations: ["postgresql"]
  tables: ["*"]
  
  spec:
    regions: 
      - "us-east-1"
      - "us-west-2"
      - "eu-west-1"
    
    # Enhanced tag collection
    enable_detailed_tag_collection: true
    
    # Resource-specific configurations
    resources:
      - "ec2_instances"
      - "rds_db_instances" 
      - "s3_buckets"
      - "lambda_functions"
      - "ecs_services"
      - "eks_clusters"
      - "elasticache_clusters"
      - "cloudformation_stacks"
      - "iam_roles"
      - "vpc_vpcs"

---
kind: destination
spec:
  name: "postgresql"
  path: "cloudquery/postgresql"
  version: "v7.0.0"
  
  spec:
    connection_string: "${POSTGRESQL_CONN_STRING}"
    schema: "aws_inventory"
```

## Resource Queries by Organizational Unit Type

### 1. Find All Resources Owned by Projects

```sql
-- File: queries/resources_by_projects.sql
SELECT 
    r.account_id,
    r.region,
    r.arn,
    r.resource_type,
    r.tags->>'OrganizationId' as organization_id,
    r.tags->>'UnitName' as unit_name,
    r.tags->>'CostCenter' as cost_center,
    r.tags->>'BudgetCode' as budget_code,
    r.tags->>'AccessLevel' as access_level,
    r.creation_date,
    CASE 
        WHEN r.tags->>'Environment' = 'Production' THEN 'PROD'
        WHEN r.tags->>'Environment' = 'Staging' THEN 'STAGE' 
        WHEN r.tags->>'Environment' = 'Development' THEN 'DEV'
        ELSE 'UNKNOWN'
    END as environment
FROM (
    -- EC2 Instances
    SELECT 
        account_id,
        region,
        arn,
        'EC2::Instance' as resource_type,
        tags,
        launch_time as creation_date
    FROM aws_ec2_instances
    WHERE tags->>'UnitType' = 'Project'
    
    UNION ALL
    
    -- RDS Instances  
    SELECT 
        account_id,
        region,
        arn,
        'RDS::DBInstance' as resource_type,
        tags,
        instance_create_time as creation_date
    FROM aws_rds_db_instances
    WHERE tags->>'UnitType' = 'Project'
    
    UNION ALL
    
    -- S3 Buckets
    SELECT 
        account_id,
        region,
        arn,
        'S3::Bucket' as resource_type,
        tags,
        creation_date
    FROM aws_s3_buckets 
    WHERE tags->>'UnitType' = 'Project'
    
    UNION ALL
    
    -- Lambda Functions
    SELECT 
        account_id,
        region,
        arn,
        'Lambda::Function' as resource_type,
        tags,
        last_modified::timestamp as creation_date
    FROM aws_lambda_functions
    WHERE tags->>'UnitType' = 'Project'
    
) r
WHERE r.tags->>'OrganizationId' IS NOT NULL
ORDER BY r.tags->>'UnitName', r.resource_type, r.creation_date DESC;
```

### 2. Find Resources by Access Level Classification

```sql
-- File: queries/resources_by_access_level.sql
WITH classified_resources AS (
    SELECT 
        account_id,
        region,
        arn,
        resource_type,
        tags->>'AccessLevel' as access_level,
        tags->>'UnitType' as unit_type,
        tags->>'UnitName' as unit_name,
        tags->>'OrganizationId' as organization_id,
        creation_date
    FROM (
        SELECT account_id, region, arn, 'EC2::Instance' as resource_type, 
               tags, launch_time as creation_date
        FROM aws_ec2_instances
        
        UNION ALL
        
        SELECT account_id, region, arn, 'RDS::DBInstance' as resource_type,
               tags, instance_create_time as creation_date  
        FROM aws_rds_db_instances
        
        UNION ALL
        
        SELECT account_id, region, arn, 'S3::Bucket' as resource_type,
               tags, creation_date
        FROM aws_s3_buckets
    ) all_resources
    WHERE tags->>'AccessLevel' IS NOT NULL
)

SELECT 
    access_level,
    unit_type,
    COUNT(*) as resource_count,
    COUNT(DISTINCT organization_id) as unique_org_units,
    ARRAY_AGG(DISTINCT resource_type) as resource_types
FROM classified_resources
WHERE access_level IN ('Public', 'Internal', 'Confidential', 'Restricted', 'Highly Restricted')
GROUP BY access_level, unit_type
ORDER BY 
    CASE access_level
        WHEN 'Highly Restricted' THEN 1
        WHEN 'Restricted' THEN 2  
        WHEN 'Confidential' THEN 3
        WHEN 'Internal' THEN 4
        WHEN 'Public' THEN 5
    END,
    unit_type;
```

### 3. Find Resources by Specific Organizational Unit

```sql
-- File: queries/resources_by_org_unit.sql
-- Parameters: organization_id (e.g., 'PROJ-ECP-001')

WITH org_unit_resources AS (
    SELECT * FROM (
        SELECT account_id, region, arn, instance_id as resource_id,
               'EC2::Instance' as resource_type, tags, 
               instance_type as resource_size, state->>'Name' as status,
               launch_time as creation_date
        FROM aws_ec2_instances
        WHERE tags->>'OrganizationId' = $1
        
        UNION ALL
        
        SELECT account_id, region, arn, db_instance_identifier as resource_id,
               'RDS::DBInstance' as resource_type, tags,
               db_instance_class as resource_size, db_instance_status as status,
               instance_create_time as creation_date
        FROM aws_rds_db_instances  
        WHERE tags->>'OrganizationId' = $1
        
        UNION ALL
        
        SELECT account_id, region, arn, name as resource_id,
               'S3::Bucket' as resource_type, tags,
               NULL as resource_size, 'Active' as status,
               creation_date
        FROM aws_s3_buckets
        WHERE tags->>'OrganizationId' = $1
        
        UNION ALL
        
        SELECT account_id, region, arn, function_name as resource_id,
               'Lambda::Function' as resource_type, tags,
               CONCAT(memory_size::text, 'MB') as resource_size, 
               state as status,
               last_modified::timestamp as creation_date
        FROM aws_lambda_functions
        WHERE tags->>'OrganizationId' = $1
        
        UNION ALL
        
        SELECT account_id, region, arn, cluster_name as resource_id,
               'EKS::Cluster' as resource_type, tags,
               NULL as resource_size, status,
               created_at as creation_date
        FROM aws_eks_clusters
        WHERE tags->>'OrganizationId' = $1
        
    ) all_resources
)

SELECT 
    resource_type,
    COUNT(*) as count,
    ARRAY_AGG(resource_id ORDER BY creation_date DESC) as resource_ids,
    MIN(creation_date) as oldest_resource,
    MAX(creation_date) as newest_resource,
    COUNT(DISTINCT region) as regions_used,
    ARRAY_AGG(DISTINCT status) as statuses
FROM org_unit_resources
GROUP BY resource_type
ORDER BY count DESC;
```

### 4. Cost Analysis by Organizational Units

```sql
-- File: queries/cost_analysis_by_org_units.sql
-- Requires AWS Cost and Usage Report data

WITH tagged_costs AS (
    SELECT 
        line_item_resource_id,
        product_product_name,
        line_item_usage_type,
        resource_tags_user_organization_id as organization_id,
        resource_tags_user_unit_type as unit_type,
        resource_tags_user_unit_name as unit_name,
        resource_tags_user_cost_center as cost_center,
        resource_tags_user_budget_code as budget_code,
        resource_tags_user_access_level as access_level,
        line_item_usage_start_date::date as usage_date,
        line_item_unblended_cost::decimal as cost,
        line_item_usage_amount::decimal as usage_amount
    FROM aws_cur_line_items
    WHERE bill_billing_period_start_date >= CURRENT_DATE - INTERVAL '30 days'
        AND resource_tags_user_organization_id IS NOT NULL
        AND line_item_line_item_type = 'Usage'
),

cost_summary AS (
    SELECT 
        unit_type,
        unit_name,
        organization_id,
        cost_center,
        budget_code,
        COUNT(DISTINCT line_item_resource_id) as resource_count,
        SUM(cost) as total_cost,
        AVG(cost) as avg_daily_cost,
        COUNT(DISTINCT product_product_name) as service_types_used
    FROM tagged_costs
    GROUP BY unit_type, unit_name, organization_id, cost_center, budget_code
)

SELECT 
    unit_type,
    unit_name,
    organization_id,
    cost_center,
    budget_code,
    resource_count,
    ROUND(total_cost, 2) as total_cost_usd,
    ROUND(avg_daily_cost, 2) as avg_daily_cost_usd,
    service_types_used,
    ROUND(100.0 * total_cost / SUM(total_cost) OVER(), 2) as cost_percentage
FROM cost_summary
WHERE total_cost > 0
ORDER BY total_cost DESC;
```

### 5. Compliance and Governance Reporting

```sql
-- File: queries/governance_compliance_report.sql
WITH resource_compliance AS (
    SELECT 
        account_id,
        region,
        arn,
        resource_type,
        tags->>'OrganizationId' IS NOT NULL as has_org_id,
        tags->>'UnitType' IS NOT NULL as has_unit_type,
        tags->>'CostCenter' IS NOT NULL as has_cost_center,
        tags->>'BudgetCode' IS NOT NULL as has_budget_code,
        tags->>'AccessLevel' IS NOT NULL as has_access_level,
        tags->>'AccessLevel' as access_level,
        tags->>'UnitType' as unit_type,
        tags->>'GovernancePolicy' as governance_policy
    FROM (
        SELECT account_id, region, arn, 'EC2::Instance' as resource_type, tags
        FROM aws_ec2_instances
        
        UNION ALL
        
        SELECT account_id, region, arn, 'RDS::DBInstance' as resource_type, tags
        FROM aws_rds_db_instances
        
        UNION ALL
        
        SELECT account_id, region, arn, 'S3::Bucket' as resource_type, tags
        FROM aws_s3_buckets
        
        UNION ALL
        
        SELECT account_id, region, arn, 'Lambda::Function' as resource_type, tags
        FROM aws_lambda_functions
        
    ) all_resources
),

compliance_summary AS (
    SELECT 
        resource_type,
        unit_type,
        access_level,
        COUNT(*) as total_resources,
        SUM(CASE WHEN has_org_id THEN 1 ELSE 0 END) as with_org_id,
        SUM(CASE WHEN has_unit_type THEN 1 ELSE 0 END) as with_unit_type,
        SUM(CASE WHEN has_cost_center THEN 1 ELSE 0 END) as with_cost_center,
        SUM(CASE WHEN has_budget_code THEN 1 ELSE 0 END) as with_budget_code,
        SUM(CASE WHEN has_access_level THEN 1 ELSE 0 END) as with_access_level,
        SUM(CASE WHEN has_org_id AND has_unit_type AND has_cost_center 
                      AND has_budget_code AND has_access_level 
                 THEN 1 ELSE 0 END) as fully_compliant
    FROM resource_compliance
    GROUP BY resource_type, unit_type, access_level
)

SELECT 
    resource_type,
    unit_type,
    access_level,
    total_resources,
    fully_compliant,
    ROUND(100.0 * fully_compliant / total_resources, 1) as compliance_percentage,
    ROUND(100.0 * with_org_id / total_resources, 1) as org_id_compliance,
    ROUND(100.0 * with_cost_center / total_resources, 1) as cost_center_compliance,
    ROUND(100.0 * with_access_level / total_resources, 1) as access_level_compliance
FROM compliance_summary
WHERE total_resources > 0
ORDER BY compliance_percentage ASC, total_resources DESC;
```
