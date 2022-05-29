import requests
import json
import os

GIT_API_BASE_URL = "https://api.github.com"
TOKEN=os.environ.get('GIT_TOKEN')

def get_stacks(repo):
    ''' Returns the languages used in the repo '''
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
    ''' Returns the contibuters' username of the repo '''

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
    ''' The function checks if the git handle/account exists and if the account is owned by the email'''
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
    ''' The function checks if the git repo exists and is public'''
    url = f"{GIT_API_BASE_URL}/repos/{repo}" 
    headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization' : f'token {TOKEN}'}
    resp = requests.get(
            url,
            headers=headers
       )
    return resp.status_code == 200
