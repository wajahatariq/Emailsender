import sqlite3
import json

DB_NAME = "/tmp/flowmotive_queue.db" # Note: /tmp is used for serverless compatibility, but resets on Vercel.

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            data_json TEXT,
            template TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_to_queue(email, data_dict, template, priority):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO email_queue (email, data_json, template, priority) VALUES (?, ?, ?, ?)',
              (email, json.dumps(data_dict), template, priority))
    conn.commit()
    conn.close()

def get_next_pending():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Prioritizes priority=1 (website_has_google_tag == True)
    c.execute("SELECT * FROM email_queue WHERE status = 'pending' ORDER BY priority DESC, id ASC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def mark_as_sent(row_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE email_queue SET status = 'sent' WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()