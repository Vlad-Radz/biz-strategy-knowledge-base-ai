docker run \
    --restart always \
    --publish=7474:7474 \
    --publish=7687:7687  \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_PLUGINS='["apoc", "n10s", "bloom", "graph-data-science"]' \
    --env NEO4J_AUTH=neo4j/testtest \
    neo4j:5.20.0