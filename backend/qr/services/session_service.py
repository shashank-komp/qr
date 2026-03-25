import json
import os
from asgiref.sync import sync_to_async
from tools_box.redisclient.cache.client import CoreRedisCacheClient
from dotenv import load_dotenv

load_dotenv()

CACHE_TIMEOUT = int(os.environ.get("CACHE_TIMEOUT", 2100))
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
MAX_CONNECTIONS = int(os.environ.get("MAX_CONNECTIONS", 2))

redis_client = CoreRedisCacheClient(url=REDIS_URL)

class SessionService:

    # API
    @staticmethod
    def create_session(room_id):
        redis_client.set(f"qr_session_count_{room_id}", 0, ex=CACHE_TIMEOUT, nx=True)

    #websocket    

    @staticmethod
    @sync_to_async
    def increment_connection_count(room_id):
        
        key = f"qr_session_count_{room_id}"
        
        if not redis_client.redis_client.exists(key):
            raise ValueError("Invalid QR Session")
            
        return redis_client.redis_client.incr(key)

    @staticmethod
    @sync_to_async
    def decrement_connection_count(room_id):
        return redis_client.redis_client.decr(f"qr_session_count_{room_id}")

    @staticmethod
    @sync_to_async
    def mark_session_active(room_id):
        redis_client.set(f"qr_session_active_{room_id}", "true", ex=CACHE_TIMEOUT)

    @staticmethod
    @sync_to_async
    def update_session_data(room_id, incoming_data):
        key = f"qr_session_data_{room_id}"
        
        if incoming_data:
            # Drop the whole dictionary into redis hashes instantaneously without JSON!
            redis_client.redis_client.hset(key, mapping=incoming_data)
            # Hashes don't take `ex` directly in `hset`, so we just touch the expiry natively
            redis_client.redis_client.expire(key, CACHE_TIMEOUT)
            
        # Retrieve the newly merged hash object using hgetall
        raw_hash = redis_client.redis_client.hgetall(key)
        
        # Redis might return byte strings (e.g. b'contact_id'), so we decode them safely back to standard strings for the frontend
        return {
            (k.decode('utf-8') if isinstance(k, bytes) else k): (v.decode('utf-8') if isinstance(v, bytes) else v)
            for k, v in raw_hash.items()
        }

    @staticmethod
    @sync_to_async
    def clear_session(room_id):
       
        keys = [
            f"qr_session_active_{room_id}",
            f"qr_session_count_{room_id}",
            f"qr_session_data_{room_id}"
        ]
        
        redis_client.redis_client.delete(*keys)