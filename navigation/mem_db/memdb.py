import redis

class MemDB:
    def __init__(self):
        self.redis = redis.Redis( 'localhost', '6379' )
        print(self.redis)