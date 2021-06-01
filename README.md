# scale-ai-traffic-signs-quality-checks
## Problem: Writing 1 quality check that can flag potential errors
## Solutions
0. Setup
```
# Using requests
url = "https://api.scale.com/v1/tasks"
querystring = {"project":"Traffic Sign Detection"}
headers = {"Accept": "application/json"}

response = requests.get(url, auth=HTTPBasicAuth(os.getenv('LIVE_API_KEY'), 'pass'), headers=headers, params=querystring)
tasks = response.json()["docs"]
```
1. Task Retrieval 
```
# Retrieve the task responses
task_responses = [task["response"] for task in tasks]
print(f"Task Responses List: {task_responses}\n\n{len(task_responses)} responses retrieved\n")

# Retrieve the original images
task_images = [task["params"]["attachment"] for task in tasks]
print(f"Task Images List: {task_images}\n\n{len(task_images)} images retrieved\n")
```
2. Programmatic Quality Checks
  - Write code that can ingest a task response, perform a quality check
  - Output a .csv or JSON file of any issues your quality check found
  - Quality checks architecture:
      - If the label isn't "non_visible_face" and the attribute's background_color is "not_applicable", then flag an "error".
      - If both width and height of the box is larger than 95% of all the boxes, then flag a "warning".
