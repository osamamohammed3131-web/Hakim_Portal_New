import secrets
def new_token(): return secrets.token_urlsafe(32)
def mask_id(v):
    return v if len(v) <= 4 else v[:2] + "*"*(len(v)-4) + v[-2:]
