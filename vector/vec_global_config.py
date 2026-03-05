### Global Config for VectorDB 
class VecGlobalConfig:
    def __init__(self,  host="localhost", port=6333, collection_name="llmsqler"):
        self.host = host
        self.port = port
        self.collection_name = collection_name

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"
    
    @property
    def collection_url(self):
        return f"{self.url}/collections/{self.collection_name}"
    
    @property
    def items_url(self):
        return f"{self.url}/items"

    def __str__(self):
        return f"VecGlobalConfig(host={self.host}, port={self.port}, collection_name={self.collection_name})"