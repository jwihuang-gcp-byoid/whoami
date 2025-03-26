import base64
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

def get_user_info_from_header(request: Request):
    principal_header = request.headers.get("X-MS-CLIENT-PRINCIPAL")
    if not principal_header:
        return None
    try:
        decoded_bytes = base64.b64decode(principal_header)
        decoded_str = decoded_bytes.decode("utf-8")
        return json.loads(decoded_str)
    except Exception as e:
        print(f"Error decoding header: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user_info = get_user_info_from_header(request)
    if user_info is None:
        return HTMLResponse(
            content="<html><body><h1>Authentication Error: No user info found.</h1></body></html>",
            status_code=401
        )
    user_details = json.dumps(user_info, indent=2)
    return HTMLResponse(
        content=f"""
        <html>
            <body>
                <h1>Welcome!</h1>
                <h2>Your User Information</h2>
                <pre>{user_details}</pre>
            </body>
        </html>
        """,
        status_code=200
    )

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)