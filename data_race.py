import time

def balance_key(gh, username):
    return 'balance.%s.%s' % (gh, username)

class RacyBalances:
    def __init__(self, redis, default, delay):
        self.redis = redis
        self.default = default
        self.delay = delay
    def get(self, gh, username):
        return int(self.redis.get(balance_key(gh, username)) or self.default)
    def put(self, gh, username, balance):
        self.redis.set(balance_key(gh, username), balance)
    def transfer(self, gh, from_username, to_username):
        b = self.get(gh, from_username)
        ob = self.get(gh, to_username)
        self.put(gh, to_username, ob + b)
        time.sleep(self.delay)
        self.put(gh, from_username, 0)


