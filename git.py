import requests
import json
import os

GIT_API_BASE_URL = "https://api.github.com"
TOKEN=os.environ.get('GIT_TOKEN')

def get_stacks(repo):
    
    url = f"{GIT_API_BASE_URL}/repos/{repo}/languages"
    headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization' : f'token {TOKEN}'}
    resp = requests.get(
            url,
            headers=headers
       )

    if resp.status_code == 200:
        return [r for r in resp.json().keys()]

    else:
        return False
   
    


    

def get_collaborators(repo):
    url = f"{GIT_API_BASE_URL}/repos/{repo}/contributors"
    headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization' : f'token {TOKEN}'}
    resp = requests.get(
            url,
            headers=headers
       )
    
    if resp.status_code == 200:
        contributors = [r["login"] for r in resp.json()]
        return contributors

    else:
        return False

    


def validate_git_handle_ownership(handle, email, is_org):
    url = f"{GIT_API_BASE_URL}/orgs/{handle}" if is_org else  f"{GIT_API_BASE_URL}/users/{handle}"
    headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization' : f'token {TOKEN}'}
    resp = requests.get(
            url,
            headers=headers
       )
    if resp.status_code == 200:
        return resp.json()["email"] == email

    else:
        return False


def validate_repo_existence(repo):
    url = f"{GIT_API_BASE_URL}/repos/{repo}" 
    headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization' : f'token {TOKEN}'}
    resp = requests.get(
            url,
            headers=headers
       )
    return resp.status_code == 200
