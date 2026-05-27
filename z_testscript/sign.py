import hmac, hashlib

secret = "my-webhook-secret"  # muss exakt wie in .env sein
body = open("payload.json", "rb").read()
digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
print("sha256=" + digest)
