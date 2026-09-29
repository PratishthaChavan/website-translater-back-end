import time


class TokenBucket:

    def __init__(
        self,
        capacity,
        refill_rate
    ):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def refill(self):

        now = time.time()

        elapsed = (
            now - self.last_refill
        )

        new_tokens = (
            elapsed * self.refill_rate
        )

        self.tokens = min(
            self.capacity,
            self.tokens + new_tokens
        )

        self.last_refill = now

    def consume(self):

        self.refill()

        if self.tokens >= 1:

            self.tokens -= 1

            return True

        return False


buckets = {}


def get_bucket(client_id):
    print("this is a client id",client_id)
    if client_id not in buckets:

        buckets[client_id] = TokenBucket(
            capacity=5,
            refill_rate=1 / 12
        )
    return buckets[client_id]
def allow_request(client_id):

    bucket = get_bucket(
        client_id
    )
    print("this is a bucket",bucket)

    return bucket.consume()