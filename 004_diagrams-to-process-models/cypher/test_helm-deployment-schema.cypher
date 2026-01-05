// Neo4j Cypher Schema for Helm Chart Hierarchy - ArgoCD WebApp Deployments
// Generated from PlantUML component diagram

// ===================================
// CREATE CONSTRAINTS
// ===================================

CREATE CONSTRAINT platform_name IF NOT EXISTS FOR (p:Platform) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT repository_name IF NOT EXISTS FOR (r:Repository) REQUIRE r.name IS UNIQUE;
CREATE CONSTRAINT component_name IF NOT EXISTS FOR (c:Component) REQUIRE c.name IS UNIQUE;

// ===================================
// CREATE PLATFORMS
// ===================================

CREATE (jfrog:Platform {
    name: 'JFrog',
    type: 'package-registry',
    url: 'https://jfrog.company.com',
    description: 'Artifact repository for Helm charts'
});

CREATE (bitbucket:Platform {
    name: 'Bitbucket',
    type: 'source-control',
    url: 'https://bitbucket.company.com',
    description: 'Git source code repository'
});

// ===================================
// CREATE REPOSITORIES (Git)
// ===================================

CREATE (gitEso:Repository {
    name: 'webapp-eso',
    type: 'helm-chart',
    description: 'Helm Chart of External Secrets Operator (ESO)',
    platform: 'bitbucket',
    language: 'yaml'
});

CREATE (gitWebApp:Repository {
    name: 'webapp-deploy',
    type: 'helm-chart', 
    description: 'Helm Chart of WebApp',
    platform: 'bitbucket',
    language: 'yaml'
});

CREATE (gitLogstash:Repository {
    name: 'webapp-logstash',
    type: 'helm-chart',
    description: 'Helm Chart of LogStash',
    platform: 'bitbucket',
    language: 'yaml'
});

CREATE (gitApplication:Repository {
    name: 'webapp_application',
    type: 'application-config',
    description: 'ArgoCD GitOps repository: central repository, where ArgoCD applications are defined',
    platform: 'bitbucket',
    language: 'yaml'
});

// ===================================
// CREATE COMPONENTS (Helm Charts)
// ===================================

CREATE (helmWebApp:Component {
    name: 'webapp-deploy',
    type: 'helm',
    version: 'latest',
    registry: 'jfrog',
    description: 'Packaged Helm chart for WebApp deployment'
});

CREATE (helmEso:Component {
    name: 'webapp-eso', 
    type: 'helm',
    version: 'latest',
    registry: 'jfrog',
    description: 'Packaged Helm chart for External Secrets Operator'
});

CREATE (helmLogstash:Component {
    name: 'webapp-logstash',
    type: 'helm',
    version: 'latest', 
    registry: 'jfrog',
    description: 'Packaged Helm chart for LogStash'
});


// ===================================
// CREATE RELATIONSHIPS
// ===================================

// Platform CONTAINS relationships
MATCH (jfrog:Platform {name: 'JFrog'}), (helmWebApp:Component {name: 'webapp-deploy'})
CREATE (jfrog)-[:CONTAINS {createdDate: datetime()}]->(helmWebApp);

MATCH (jfrog:Platform {name: 'JFrog'}), (helmEso:Component {name: 'webapp-eso'})
CREATE (jfrog)-[:CONTAINS {createdDate: datetime()}]->(helmEso);

MATCH (jfrog:Platform {name: 'JFrog'}), (helmLogstash:Component {name: 'webapp-logstash'})
CREATE (jfrog)-[:CONTAINS {createdDate: datetime()}]->(helmLogstash);

MATCH (bitbucket:Platform {name: 'Bitbucket'}), (gitEso:Repository {name: 'webapp-eso'})
CREATE (bitbucket)-[:CONTAINS {createdDate: datetime()}]->(gitEso);

MATCH (bitbucket:Platform {name: 'Bitbucket'}), (gitWebApp:Repository {name: 'webapp-deploy'})
CREATE (bitbucket)-[:CONTAINS {createdDate: datetime()}]->(gitWebApp);

MATCH (bitbucket:Platform {name: 'Bitbucket'}), (gitLogstash:Repository {name: 'webapp-logstash'})
CREATE (bitbucket)-[:CONTAINS {createdDate: datetime()}]->(gitLogstash);

MATCH (bitbucket:Platform {name: 'Bitbucket'}), (gitApplication:Repository {name: 'webapp_application'})
CREATE (bitbucket)-[:CONTAINS {createdDate: datetime()}]->(gitApplication);

// REFERS relationships (gitApplication refers to helm charts)
// Fixed: Use WHERE clause to ensure nodes exist before creating relationships
MATCH (gitApplication:Repository {name: 'webapp_application'})
MATCH (helmWebApp:Component {name: 'webapp-deploy'})
WHERE gitApplication IS NOT NULL AND helmWebApp IS NOT NULL
CREATE (gitApplication)-[:REFERS {referenceType: 'dependency', version: 'latest'}]->(helmWebApp);

MATCH (gitApplication:Repository {name: 'webapp_application'})
MATCH (helmEso:Component {name: 'webapp-eso'})
WHERE gitApplication IS NOT NULL AND helmEso IS NOT NULL
CREATE (gitApplication)-[:REFERS {referenceType: 'dependency', version: 'latest'}]->(helmEso);

MATCH (gitApplication:Repository {name: 'webapp_application'})
MATCH (helmLogstash:Component {name: 'webapp-logstash'})
WHERE gitApplication IS NOT NULL AND helmLogstash IS NOT NULL
CREATE (gitApplication)-[:REFERS {referenceType: 'dependency', version: 'latest'}]->(helmLogstash);

// PUBLISHED_FROM relationships (helm charts published from git repos)
MATCH (helmWebApp:Component {name: 'webapp-deploy'}), (gitWebApp:Repository {name: 'webapp-deploy'})
CREATE (helmWebApp)-[:PUBLISHED_FROM {publishDate: datetime(), buildNumber: 'build-001'}]->(gitWebApp);

MATCH (helmEso:Component {name: 'webapp-eso'}), (gitEso:Repository {name: 'webapp-eso'})
CREATE (helmEso)-[:PUBLISHED_FROM {publishDate: datetime(), buildNumber: 'build-002'}]->(gitEso);

MATCH (helmLogstash:Component {name: 'webapp-logstash'}), (gitLogstash:Repository {name: 'webapp-logstash'})
CREATE (helmLogstash)-[:PUBLISHED_FROM {publishDate: datetime(), buildNumber: 'build-003'}]->(gitLogstash);

// ===================================
// LOGICAL FIXES AND IMPROVEMENTS
// ===================================

// Add missing indexes for better performance
CREATE INDEX repository_type IF NOT EXISTS FOR (r:Repository) ON (r.type);
CREATE INDEX component_type IF NOT EXISTS FOR (p:Component) ON (p.type);
CREATE INDEX platform_type IF NOT EXISTS FOR (pl:Platform) ON (pl.type);
