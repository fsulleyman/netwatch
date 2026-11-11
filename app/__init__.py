import os
import secrets
from flask import request, Response

@app.before_request
def require_login():
    user = os.environ.get("NETWATCH_USER", "admin")
    password = os.environ.get("NETWATCH_PASSWORD")
    if not password:
        return Response("Server is not configured.", 503)

    auth = request.authorization
    ok = (
        auth is not None
        and secrets.compare_digest(auth.username, user)
        and secrets.compare_digest(auth.password or "", password)
    )
    if not ok:
        return Response("Login required", 401,
                        {"WWW-Authenticate": 'Basic realm="NetWatch"'})