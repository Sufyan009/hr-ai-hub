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
    # Try to extract error details from backend
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    msg = f'Failed to update candidate {candidate_id}.'
    if detail:
        msg += f' Reason: {detail}'
    return {"success": False, "message": msg}

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

def add_candidate(data, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/'
    r = requests.post(url, json=data, headers=headers)
    if r.status_code in (200, 201):
        return {"success": True, "message": "Candidate added successfully.", "candidate": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to add candidate. Reason: {detail}"}

def add_note(candidate_id, content, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/notes/'
    data = {"candidate": candidate_id, "content": content}
    r = requests.post(url, json=data, headers=headers)
    if r.status_code in (200, 201):
        return {"success": True, "message": "Note added successfully.", "note": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to add note. Reason: {detail}"}

def list_notes(candidate_id, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/notes/?candidate={candidate_id}'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response_data = r.json()
        # Handle both paginated and non-paginated responses
        if isinstance(response_data, dict) and 'results' in response_data:
            notes = response_data['results']
        else:
            notes = response_data
        return {"success": True, "notes": notes}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch notes. Reason: {detail}"}

def delete_note(note_id, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/notes/{note_id}/'
    r = requests.delete(url, headers=headers)
    if r.status_code == 204:
        return {"success": True, "message": "Note deleted successfully."}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to delete note. Reason: {detail}"}

def list_job_titles(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/jobtitles/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response_data = r.json()
        # Handle both paginated and non-paginated responses
        if isinstance(response_data, dict) and 'results' in response_data:
            job_titles = response_data['results']
        else:
            job_titles = response_data
        return {"success": True, "job_titles": job_titles}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch job titles. Reason: {detail}"}

def list_cities(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/cities/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response_data = r.json()
        # Handle both paginated and non-paginated responses
        if isinstance(response_data, dict) and 'results' in response_data:
            cities = response_data['results']
        else:
            cities = response_data
        return {"success": True, "cities": cities}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch cities. Reason: {detail}"}

def list_sources(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/sources/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response_data = r.json()
        # Handle both paginated and non-paginated responses
        if isinstance(response_data, dict) and 'results' in response_data:
            sources = response_data['results']
        else:
            sources = response_data
        return {"success": True, "sources": sources}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch sources. Reason: {detail}"}

def list_communication_skills(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/communicationskills/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        response_data = r.json()
        # Handle both paginated and non-paginated responses
        if isinstance(response_data, dict) and 'results' in response_data:
            communication_skills = response_data['results']
        else:
            communication_skills = response_data
        return {"success": True, "communication_skills": communication_skills}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch communication skills. Reason: {detail}"}

def export_candidates_csv(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/export/csv/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return {"success": True, "csv": r.text}
    return {"success": False, "message": "Failed to export candidates as CSV."}

def get_recent_activities(auth_token=None, limit=10):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/recent-activities/?limit={limit}'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return {"success": True, "activities": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch recent activities. Reason: {detail}"}

def get_overall_metrics(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/metrics/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return {"success": True, "metrics": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch overall metrics. Reason: {detail}"}

def get_candidate_metrics(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/metrics/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return {"success": True, "metrics": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch candidate metrics. Reason: {detail}"}

def list_job_posts(auth_token=None, params=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/jobposts/'
    r = requests.get(url, headers=headers, params=params or {})
    if r.status_code == 200:
        response_data = r.json()
        # Handle both paginated and non-paginated responses
        if isinstance(response_data, dict) and 'results' in response_data:
            job_posts = response_data['results']
        else:
            job_posts = response_data
        return {"success": True, "job_posts": job_posts}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch job posts. Reason: {detail}"}

def add_job_post(data, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/jobposts/'
    r = requests.post(url, json=data, headers=headers)
    if r.status_code in (200, 201):
        return {"success": True, "message": "Job post added successfully.", "job_post": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to add job post. Reason: {detail}"}

def update_job_post(job_post_id, data, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/jobposts/{job_post_id}/'
    r = requests.patch(url, json=data, headers=headers)
    if r.status_code == 200:
        return {"success": True, "message": "Job post updated successfully.", "job_post": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to update job post. Reason: {detail}"}

def delete_job_post(job_post_id, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/jobposts/{job_post_id}/'
    r = requests.delete(url, headers=headers)
    if r.status_code == 204:
        return {"success": True, "message": "Job post deleted successfully."}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to delete job post. Reason: {detail}"}

def get_job_post_title_choices(auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/jobposts/job-title-choices/'
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return {"success": True, "choices": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch job post title choices. Reason: {detail}"}

def get_job_post(job_post_id, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    r = requests.get(f'{DJANGO_API}/jobposts/{job_post_id}/', headers=headers)
    if r.status_code == 200:
        return r.json()
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to get job post {job_post_id}. Reason: {detail}"}

def format_job_post(job_post):
    if not job_post:
        return 'No job post details available.'
    md = f"**Job Post Details**\n\n"
    md += f"**ID:** {job_post.get('id', 'N/A')}\n"
    md += f"**Title:** {job_post.get('title', 'N/A')}\n"
    md += f"**Department:** {job_post.get('department', 'N/A')}\n"
    md += f"**Location:** {job_post.get('location', 'N/A')}\n"
    md += f"**Status:** {job_post.get('status', 'N/A')}\n"
    md += f"**Description:** {job_post.get('description', 'N/A')}\n"
    md += f"**Requirements:** {job_post.get('requirements', 'N/A')}\n"
    md += f"**Salary Range:** {job_post.get('salary_range', 'N/A')}\n"
    md += f"**Created At:** {job_post.get('created_at', 'N/A')}\n"
    md += f"**Updated At:** {job_post.get('updated_at', 'N/A')}\n"
    return md

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
        # Skills: prefer communication_skills_detail.name, fallback to skills or communication_skills
        skills = ''
        if c.get('communication_skills_detail') and c['communication_skills_detail'].get('name'):
            skills = c['communication_skills_detail']['name']
        elif c.get('skills'):
            skills = ', '.join(c['skills']) if isinstance(c['skills'], list) else str(c['skills'])
        elif c.get('communication_skills'):
            skills = ', '.join(c['communication_skills']) if isinstance(c['communication_skills'], list) else str(c['communication_skills'])
        # Location: prefer city_detail.name, fallback to city
        location = ''
        if c.get('city_detail') and c['city_detail'].get('name'):
            location = c['city_detail']['name']
        elif c.get('city'):
            location = str(c['city'])
        rows.append([
            c.get('id', ''),
            c.get('name', c.get('first_name', '')),
            c.get('email', ''),
            c.get('status', c.get('candidate_stage', '')),
            skills,
            str(c.get('experience', c.get('years_of_experience', ''))),
            location,
        ])
    md = '| ' + ' | '.join(headers) + ' |\n'
    md += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
    for row in rows:
        md += '| ' + ' | '.join(str(cell) for cell in row) + ' |\n'
    return md 

def search_candidates(filters=None, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/'
    r = requests.get(url, headers=headers, params=filters or {})
    if r.status_code == 200:
        response_data = r.json()
        # Handle both paginated and non-paginated responses
        if isinstance(response_data, dict) and 'results' in response_data:
            candidates = response_data['results']
        else:
            candidates = response_data
        return {"success": True, "candidates": candidates}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to search candidates. Reason: {detail}"}

def bulk_update_candidates(ids, field, value, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    results = []
    for cid in ids:
        r = requests.patch(f'{DJANGO_API}/candidates/{cid}/', json={field: value}, headers=headers)
        if r.status_code == 200:
            results.append({"id": cid, "success": True})
        else:
            try:
                err = r.json()
                detail = err.get('detail') or err.get('message') or str(err)
            except Exception:
                detail = r.text
            results.append({"id": cid, "success": False, "message": detail})
    return results

def bulk_delete_candidates(ids, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    results = []
    for cid in ids:
        r = requests.delete(f'{DJANGO_API}/candidates/{cid}/', headers=headers)
        if r.status_code == 204:
            results.append({"id": cid, "success": True})
        else:
            try:
                err = r.json()
                detail = err.get('detail') or err.get('message') or str(err)
            except Exception:
                detail = r.text
            results.append({"id": cid, "success": False, "message": detail})
    return results 