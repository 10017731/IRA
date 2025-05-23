import os, base64, tempfile
from fastapi import FastAPI, HTTPException
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = FastAPI()

# ─── 1. Read & write service account key ─────────────────────
b64 = os.getenv("GOOGLE_SERVICE_KEY_B64")
if not b64:
    raise RuntimeError("Missing GOOGLE_SERVICE_KEY_B64")
data = base64.b64decode(b64)
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
tmp.write(data)
tmp.flush()
KEY_PATH = tmp.name

# ─── 2. Build Sheets client ──────────────────────────────────
creds = Credentials.from_service_account_file(
    KEY_PATH,
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
)
sheets_api = build("sheets", "v4", credentials=creds).spreadsheets()

# ─── 3. Health check ─────────────────────────────────────────
@app.get("/ping")
async def ping():
    return {"pong": True}

# ─── 4. Single-range fetch ────────────────────────────────────
@app.get("/sheet/{spreadsheet_id}/{range}")
async def get_sheet(spreadsheet_id: str, range: str):
    try:
        result = sheets_api.values().get(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()
        return {"values": result.get("values", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─── 5. Full-workbook fetch ───────────────────────────────────
@app.get("/spreadsheet/{spreadsheet_id}")
async def get_full_spreadsheet(spreadsheet_id: str):
    """
    Returns every sheet and its data in the workbook.
    """
    try:
        result = sheets_api.get(
            spreadsheetId=spreadsheet_id,
            includeGridData=True
        ).execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─── 6. Server startup ────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "sheet_bridge:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080))
    )
