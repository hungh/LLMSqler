# VectorDB

## Qdrant

### Docker

docker pull qdrant/qdrant

### Create the Named Volume


```bash
docker volume create qdrant_storage
```

### Run Qdrant

```bash
docker run -d --name qdrant --restart unless-stopped -v qdrant_storage:/qdrant/storage -p 6333:6333 qdrant/qdrant
```

### Launch Qdrant Dashboard

http://localhost:6333/dashboard#/welcome
