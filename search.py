
import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, 'jira.env'))

jira_domain = os.getenv('jira_domain')
jira_pat = os.getenv('jira_pat')
jira_email = os.getenv('jira_email')

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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search Jira issues")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_get = sub.add_parser("get", help="get one issue by key")
    p_get.add_argument("key")

    p_q = sub.add_parser("query", help="query issues in a project with JQL")
    p_q.add_argument("project")
    p_q.add_argument("jql_filter")
    p_q.add_argument("--max", type=int, default=25)

    args = parser.parse_args()
    if args.cmd == "get":
        print(get_issue(args.key))
    else:
        print(query_issue(args.project, args.jql_filter, args.max))
