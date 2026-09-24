import uuid

jobs = {}
def create_job():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "Processing...",
        "pages" : [],
        "complete": False
    }
    return job_id

def add_page(job_id,page_number,page_url):
    jobs[job_id]["pages"].append({
        "page" : page_number,"url":page_url
    })
    print("Page added to job:", page_number, page_url)
def complete_job(job_id):
    jobs[job_id]["status"] = "Complete"
    jobs[job_id]["complete"] = True
    
    