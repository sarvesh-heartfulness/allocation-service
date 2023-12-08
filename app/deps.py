import requests
from fastapi import Request, HTTPException, status

import os
from dotenv import load_dotenv
load_dotenv()

def is_authenticated(request: Request):
    auth_token = request.headers.get('Authorization', None)
    url = os.environ.get("MYSRCM_URL", None)
    client_id = request.headers.get("X-Client-Id", None)
    if not url:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR\
                            , "MYSRCM_URL is not configured")
    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json",
        "X-Client-Id": client_id
    }
    resp = requests.get(f"{url}api/v2/me/", headers=headers)
    if resp.status_code == status.HTTP_200_OK:
        return True
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication credentials were not provided.")
