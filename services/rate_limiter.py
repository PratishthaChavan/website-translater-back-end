import time
from services.redis_client import redis_client
TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local tokens = tonumber(redis.call("HGET", key, "tokens"))
local last_refill = tonumber(redis.call("HGET", key, "last_refill"))

if tokens == nil then
    tokens = capacity
    last_refill = now
end

local elapsed = now - last_refill

tokens = math.min(
    capacity,
    tokens + (elapsed * refill_rate)
)

local allowed = 0

if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

redis.call("HSET", key, "tokens", tokens)
redis.call("HSET", key, "last_refill", now)

redis.call("EXPIRE", key, 3600)

return {allowed, tokens}
"""

def allow_request(client_id):
    key = f"rate_limit:{client_id}"
    capacity = 5
    # 1 token every 12 seconds
    refill_rate = 1 / 12
    now = time.time()
    result = redis_client.eval(
        TOKEN_BUCKET_SCRIPT,
        1,
        key,
        capacity,
        refill_rate,
        now
    )

    allowed = int(result[0])
    remaining_tokens = float(result[1])

    return allowed == 1, remaining_tokens
