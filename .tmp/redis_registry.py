import redis
import random

# Connect to your Redis instance (likely on the Gigabyte node)
r = redis.Redis(host='gigabyte-server-ip', port=6379, db=0)

def register_parent_ids(table_name, id_list):
    """
    Initializes parent IDs with an access count of 0.
    """
    mapping = {str(uid): 0 for uid in id_list}
    if mapping:
        r.zadd(f"pool:{table_name}", mapping)

def get_batch_fk_ids(table_name, batch_size=100):
    """
    Picks the IDs with the LOWEST access counts.
    Increments their count so they aren't picked again immediately.
    """
    # 1. Fetch the 'batch_size' members with the lowest scores
    # ZRANGE with scores gives us [(id, score), ...]
    least_used = r.zrange(f"pool:{table_name}", 0, batch_size - 1, withscores=True)
    
    if not least_used:
        return []

    selected_ids = []
    pipeline = r.pipeline()
    
    for uid_bytes, score in least_used:
        uid = uid_bytes.decode('utf-8')
        selected_ids.append(uid)
        
        # 2. Increment the 'access_count' score in the ZSET
        pipeline.zincrby(f"pool:{table_name}", 1, uid)
    
    pipeline.execute()
    return selected_ids

# --- Usage in your loop ---
# 1. After inserting Users into Postgres:
# register_parent_ids('users', [uuid1, uuid2, ...])

# 2. When generating User_Roles:
# fks = get_batch_fk_ids('users', batch_size=10)