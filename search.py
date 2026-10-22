
import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import anthropic
from anthropic import beta_tool

load_dotenv('jira.env')
load_dotenv('anthropic.env')

file = open("prompt.txt", "r", encoding="utf-8")
prompt = file.read()
jira_domain = os.getenv('jira_domain')
jira_pat = os.getenv('jira_pat')
jira_email = os.getenv('jira_email')
base_url = os.getenv("ANTHROPIC_BASE_URL")
auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
default_model = os.getenv("ANTHROPIC_MODEL")
custom_headers_raw = os.getenv("ANTHROPIC_CUSTOM_HEADERS")
custom_headers = {}
if custom_headers_raw:
    try:
        custom_headers = json.loads(custom_headers_raw)
    except:
        for header in custom_headers_raw.split(","):
            if ":" in header:
                key, value = header.split(":", 1)
                custom_headers[key.strip()] = value.strip()
header = {
  "Accept": "application/json",
  "Content-Type": "application/json"
}
url = jira_domain
auth = HTTPBasicAuth(jira_email, jira_pat)

def response(query):
    x = requests.request(
        "GET",
        url,
        headers=header,
        params=query,
        auth=auth
        )
    result = x.json()

    if 'issues' not in result:
            return json.dumps({'error': result})
    formatted = []
    for issue in result['issues']:
        formatted.append({
            'key': issue['key'],
            'summary': issue['fields']['summary'],
            'type': issue['fields']['issuetype']['name'],
            'status': issue['fields']['status']['name'],
            'priority': issue['fields']['priority']['name'],
            'created': issue['fields']['created'],
            'assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
            'reporter': issue['fields']['reporter']['displayName'],
            'description': issue['fields']['description']
        })
    return json.dumps(formatted,indent=2, separators=(",",":"))

@beta_tool
def get_issue(issue_key):
    query = {
        'jql' : f'key = {issue_key}',
        'maxResults' : 1,
        'fields' : [
            'summary',
            'issuetype',
            'status',
            'priority',
            'created',
            'assignee',
            'reporter',
            'description'
        ]
    }
    return response(query)

@beta_tool
def query_issue(project, jql_filter, max):
    query = {
        'jql' : f'project = {project} AND {jql_filter}',
        'maxResults' : max if max else 25,
        'fields' : [
            'summary',
            'issuetype',
            'status',
            'priority',
            'created',
            'assignee',
            'reporter',
            'description'
        ]
    }
    return response(query)

client = anthropic.Anthropic(
    api_key=auth_token,
    base_url=base_url,
    default_headers=custom_headers
)

def jira_agent(content):
    runner = client.beta.messages.tool_runner(
        model=default_model,
        max_tokens=10000,
        tools=[get_issue, query_issue],
        messages=[
            {
                "role": 'user',
                "content": f'''
                            {prompt}
                            {content}
                            ''',
            }
        ]
    )

    for event in runner:
        if event.type == "message":
            message = event

    text_blocks = [block.text for block in message.content if block.type == "text"]
    return "\n".join(text_blocks) if text_blocks else "No response"

if __name__ == "__main__":
    while True:
        content = input("\nInput: ")
        if content.lower() == "exit":
            print("\nThank you for using Jira Agent.")
            break
        print(jira_agent(content))
