import numpy as np
import json
import os
import requests
from requests.auth import HTTPBasicAuth

def get_unusual_box_sizes():
    """
    This function returns 95th percentile widths and heights of the boxes,
    which are larger than the 95% of all the boxes we have in the project
    :return: percentile_width, percentile_height
    """

    task_annotations = [task["annotations"] for task in task_responses]
    heights = []
    widths = []

    for i in range(len(task_annotations)):
        for j in range(len(task_annotations[i])):
            dict = task_annotations[i][j]
            height = dict['height']
            heights.append(height)
            np_heights = np.array(heights)
            percentile_height = np.percentile(np_heights, 95)

            width = dict['width']
            widths.append(width)
            np_widths = np.array(widths)
            percentile_width = np.percentile(np_widths, 95)

    return percentile_width, percentile_height

# Save JSON
def save_data(*results):
   with open("results.json", "w") as f:
      json.dump(list(results), f)

# Using requests
url = "https://api.scale.com/v1/tasks"
querystring = {"project":"Traffic Sign Detection"}
headers = {"Accept": "application/json"}

"""
Phase 1. Task Retrieval:
    - Retrieve (1)the task responses and (2)the original images used are available on the public internet.
"""

response = requests.get(url, auth=HTTPBasicAuth(os.getenv('LIVE_API_KEY'), 'pass'), headers=headers, params=querystring)
tasks = response.json()["docs"]

# Retrieve the task responses
task_responses = [task["response"] for task in tasks]
print(f"Task Responses List: {task_responses}\n\n{len(task_responses)} responses retrieved\n")

# Retrieve the original images
task_images = [task["params"]["attachment"] for task in tasks]
print(f"Task Images List: {task_images}\n\n{len(task_images)} images retrieved\n")

"""
Phase 2. Programmatic Quality Checks:
    - Write code that can ingest a task response, perform a quality check
    - Output a .csv or JSON file of any issues your quality check found
    - Quality checks architecture:
        - If the label isn't "non_visible_face" AND the attribute's background_color is "not_applicable", 
            then flag an "error" with the uuid and suggest "other" for the background color.
        - If both width and height of the box is larger than 95% of all the boxes, 
            then flag a "warning".
"""

# Retrieve the task IDs
task_ids = [task["task_id"] for task in tasks]

# Retrieve task annotations
task_annotations = [task["annotations"] for task in task_responses]

# To save JSON later
results = []

# Get 95th percentile widths and heights of all the boxes in the project
unusual_box_width = get_unusual_box_sizes()[0]
unusual_box_height = get_unusual_box_sizes()[1]

# Run quality checks
for i in range(len(task_annotations)):
    image_link = task_images[i]
    task_id = task_ids[i]

    for j in range(len(task_annotations[i])):
        dict_to_test = task_annotations[i][j]
        uuid_to_flag = dict_to_test['uuid']
        label_to_flag = dict_to_test['label']
        height_to_flag = dict_to_test['height']
        width_to_flag = dict_to_test['width']

        # If the label isn't "non_visible_face" AND the attribute's background_color is "not_applicable"
        # Then flag "error: with the uuid and suggest "other" for the background color
        if dict_to_test['label'] != "non_visible_face" and dict_to_test['attributes']['background_color'] == "not_applicable":
            result = {
                "taskId": task_id,
                "uuid": uuid_to_flag,
                "label": label_to_flag,
                "height": height_to_flag,
                "width": width_to_flag,
                "image": image_link,
                "auditLink": f"https://dashboard.scale.com/audit?taskId={task_id}",
                "escalationSeverity": "error",
                "escalationMessages": "The 'not_applicable' background color should be used for the 'non_visible_face' label. Use the 'other' background color for the other labels."
            }
            results.append(result)

        # If both the width and height of the box is larger than 95% of all the boxes, then flag a warning
        elif dict_to_test['width'] > unusual_box_width and dict_to_test['height'] > unusual_box_height:
            result = {
                "taskId": task_id,
                "uuid": uuid_to_flag,
                "label": label_to_flag,
                "height": height_to_flag,
                "width": width_to_flag,
                "image": image_link,
                "auditLink": f"https://dashboard.scale.com/audit?taskId={task_id}",
                "escalationSeverity": "warning",
                "escalationMessages": "Both the width and height of the box seem unusually larger than 95% of all the boxes in the project. It seems risky but could be OK."
            }
            results.append(result)

# Output a JSON file of any issues your quality check found
save_data(results)