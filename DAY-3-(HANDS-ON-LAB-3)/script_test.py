import urllib.request
import json
import time

base_url = "http://127.0.0.1:8000/moderate"

def submit_text(text):
    print(f"\n--- Submitting Text ---")
    print(f"Payload: '{text}'")
    req = urllib.request.Request(
        f'{base_url}/submit', 
        data=json.dumps({"text": text}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        print(f"Status: {data['status']}")
        print(f"AI Score: {data['ai_score']}")
        print(f"AI Reasoning: {data['ai_reasoning']}")
        return data['job_id']
    except Exception as e:
        print(f"Error: {e}")
        return None

def submit_review(job_id, decision):
    print(f"\n--- Escalating to Human Review ---")
    print(f"Acting on Job ID: {job_id}")
    print(f"Action Taken: {decision}")
    
    data = urllib.parse.urlencode({'decision': decision}).encode('utf-8')
    req = urllib.request.Request(f'{base_url}/{job_id}/review', data=data)
    try:
        # FastAPI might reply with 303 Redirect to GET the review page again
        res = urllib.request.urlopen(req)
        print("Success! Workflow state updated and resumed.")
    except Exception as e:
        print(f"Error escalating review: {e}")

# Proceed
print(">>> INITIATING AUTOMATED PIPELINE TEST <<<\n")

# 1. Benign
submit_text("The weather is absolutely wonderful today, maybe I'll go for a walk.")

# 2. Toxic
submit_text("I hate everyone and want to destroy the world entirely.")

# 3. Ambiguous
amb_id = submit_text("I seriously demolished my programming exam today, absolute murder!")

if amb_id:
    print("\nState paused by LangGraph: Interrupted explicitly at 'human_review' node.")
    time.sleep(1)
    submit_review(amb_id, "APPROVED")
