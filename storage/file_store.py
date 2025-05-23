#reads & writes to 'data/posted_jobs.json'
#remembers the previous jobs, and it will not send notification for same job

import json
import os

def load_jobs(path='data/posted_jobs.json'):
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_jobs(data, path='data/posted_jobs.json'):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)