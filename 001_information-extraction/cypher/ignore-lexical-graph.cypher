// Get all nodes except Chunks
MATCH (n)
WHERE NOT 'Chunk' IN labels(n)
RETURN n
