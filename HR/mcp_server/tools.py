import requests

DJANGO_API = 'http://localhost:8000/api'

def get_candidate(candidate_id, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/{candidate_id}/'
    print(f"[MCP tools] get_candidate URL: {url}")
    print(f"[MCP tools] get_candidate headers: {headers}")
    r = requests.get(url, headers=headers)
    print(f"[MCP tools] get_candidate status: {r.status_code}")
    print(f"[MCP tools] get_candidate response: {r.text}")
    if r.status_code == 200:
        return r.json()
    return {"success": False, "message": f'Candidate {candidate_id} not found.'}

def delete_candidate(candidate_id, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    print("[MCP tools] delete_candidate headers:", headers)
    url = f'{DJANGO_API}/candidates/{candidate_id}/'
    r = requests.delete(url, headers=headers)
    print(f"[MCP tools] delete_candidate status: {r.status_code}")
    print(f"[MCP tools] delete_candidate response: {r.text}")
    if r.status_code == 204:
        return {"success": True, "message": f'Candidate {candidate_id} deleted successfully.'}
    # Try to extract error details from backend
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    msg = f'Failed to delete candidate {candidate_id}.'
    if detail:
        msg += f' Reason: {detail}'
    return {"success": False, "message": msg}

def update_candidate(candidate_id, field, value, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    print("[MCP tools] update_candidate headers:", headers)
    r = requests.patch(f'{DJANGO_API}/candidates/{candidate_id}/', json={field: value}, headers=headers)
    if r.status_code == 200:
        return {"success": True, "message": f'Candidate {candidate_id} updated: {field} set to {value}.'}
    return {"success": False, "message": f'Failed to update candidate {candidate_id}.'}

def get_candidate_metrics(params=None, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/metrics/'
    print(f"[MCP tools] get_candidate_metrics URL: {url}")
    print(f"[MCP tools] get_candidate_metrics headers: {headers}")
    r = requests.get(url, params=params or {}, headers=headers)
    print(f"[MCP tools] get_candidate_metrics status: {r.status_code}")
    print(f"[MCP tools] get_candidate_metrics response: {r.text}")
    if r.status_code == 200:
        return r.json()
    return {"success": False, "message": 'Failed to fetch candidate metrics.'}

def list_candidates(page=1, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/'
    print(f"[MCP tools] list_candidates URL: {url}")
    print(f"[MCP tools] list_candidates headers: {headers}")
    r = requests.get(url, params={'page': page}, headers=headers)
    print(f"[MCP tools] list_candidates status: {r.status_code}")
    print(f"[MCP tools] list_candidates response: {r.text}")
    if r.status_code == 200:
        return r.json()
    return {"success": False, "message": 'Failed to fetch candidates list.'}

# Format a single candidate dict as markdown
def format_candidate(candidate):
    # Compose a detailed markdown summary of the candidate
    name = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()
    email = candidate.get('email', '')
    phone = candidate.get('phone_number', '')
    job_title = candidate.get('job_title_detail', {}).get('name', '')
    status = candidate.get('candidate_stage', candidate.get('status', ''))
    skills = candidate.get('skills') or candidate.get('communication_skills_detail', {}).get('name', '')
    if isinstance(skills, list):
        skills = ', '.join(skills)
    city = candidate.get('city_detail', {}).get('name', '')
    source = candidate.get('source_detail', {}).get('name', '')
    experience = candidate.get('years_of_experience', candidate.get('experience', ''))
    notes = candidate.get('notes', '')
    created_at = candidate.get('created_at', '')
    
    return f"""
**{name}**
- Email: {email}
- Phone: {phone}
- Job Title: {job_title}
- Status: {status}
- Skills: {skills}
- Experience: {experience} years
- City: {city}
- Source: {source}
- Notes: {notes}
- Created At: {created_at}
"""

# Format a list of candidates as a markdown table
def format_candidate_list(candidates):
    if not candidates:
        return 'No candidates found.'
    headers = ['ID', 'Name', 'Email', 'Status', 'Skills', 'Experience', 'Location']
    rows = []
    for c in candidates:
        rows.append([
            c.get('id', ''),
            c.get('name', c.get('first_name', '')),
            c.get('email', ''),
            c.get('status', c.get('candidate_stage', '')),
            ', '.join(c.get('skills', c.get('communication_skills', []))),
            str(c.get('experience', c.get('years_of_experience', ''))),
            c.get('location', c.get('city', '')),
        ])
    md = '| ' + ' | '.join(headers) + ' |\n'
    md += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    for row in rows:
        md += '| ' + ' | '.join(row) + ' |\n'
    return md 