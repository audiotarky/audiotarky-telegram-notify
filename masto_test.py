from pathlib import Path
import json
from bot import send_mastodon

creds_file = Path("creds.json")
creds = json.loads(creds_file.read_text())

send_mastodon("How are we all today?", creds)
