from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
from .database import init_db, add_to_queue, get_next_pending, mark_as_sent, get_queue_status
from .agent import process_lead_with_agent
from .mailer import send_email

app = FastAPI(title="Flowmotive API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

@app.post("/api/upload")
async def upload_leads(
    file: UploadFile = File(...),
    template: str = Form(...)
):
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents))
    
    df = df.fillna("")
    
    records_added = 0
    for _, row in df.iterrows():
        data_dict = row.to_dict()
        email = data_dict.get("email_1")
        
        if not email:
            continue
        
        tag_status = str(data_dict.get("website_has_google_tag", "")).strip().lower()
        priority = 1 if tag_status == "true" else 0
        
        add_to_queue(email, data_dict, template, priority)
        records_added += 1
        
    return {"status": "success", "message": f"Added {records_added} leads to queue. Priority leads queued first."}

@app.get("/api/cron/process-email")
async def process_email_cron():
    next_lead = get_next_pending()
    
    if not next_lead:
        return {"status": "idle", "message": "No pending emails in queue."}
    
    lead_data = json.loads(next_lead["data_json"])
    target_email = next_lead["email"]
    template = next_lead["template"]
    
    drafted_body, subject = process_lead_with_agent(lead_data, template)
    success = send_email(target_email, subject, drafted_body)
    
    if success:
        mark_as_sent(next_lead["id"])
        return {"status": "success", "message": f"Sent email to {target_email}"}
    else:
        return {"status": "error", "message": f"Failed to send to {target_email}"}


@app.get("/api/status")
async def get_status():
    return get_queue_status()
