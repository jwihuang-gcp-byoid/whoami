import base64
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

def get_id_token_from_header(request: Request):
    principal_header = request.headers.get("X-MS-TOKEN-AAD-ID-TOKEN")
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
    id_token = get_id_token_from_header(request)
    if id_token is None:
        headers_json = json.dumps(request.headers, indent=2)
        return HTMLResponse(
            content="""
            <html>
                <body>
                    <h1>Authentication Error: No user ID token found from the header `X-MS-TOKEN-AAD-ID-TOKEN`. All headers are below:</h1>
                    <pre>{headers_json}</pre>
                </body>
            </html>
            """,
            status_code=401
        )
    user_details = json.dumps(id_token, indent=2)
    return HTMLResponse(
        content=f"""
        <html>
            <body>
                <h1>Welcome!</h1>
                <h2>Below is the clear text JWT (from X-MS-TOKEN-AAD-ID-TOKEN header) used in this azure app, which should contain the info of who you are:</h2>
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