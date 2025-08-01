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

def get_candidate_metrics(auth_token=None):
    print(f"[MCP tools] get_candidate_metrics called with auth_token: {auth_token}")
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    print(f"[MCP tools] get_candidate_metrics headers: {headers}")
    url = f'{DJANGO_API}/candidates/metrics/'
    print(f"[MCP tools] get_candidate_metrics URL: {url}")
    r = requests.get(url, headers=headers)
    print(f"[MCP tools] get_candidate_metrics status: {r.status_code}")
    print(f"[MCP tools] get_candidate_metrics response: {r.text}")
    if r.status_code == 200:
        return {"success": True, "metrics": r.json()}
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to fetch candidate metrics. Reason: {detail}"}

def list_candidates(page=1, auth_token=None, all_candidates=False):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/'
    print(f"[MCP tools] list_candidates URL: {url}")
    print(f"[MCP tools] list_candidates headers: {headers}")
    
    # If all_candidates is True, get all candidates without pagination
    if all_candidates:
        r = requests.get(url, params={'page_size': 1000}, headers=headers)  # Large page size to get all
    else:
        r = requests.get(url, params={'page': page}, headers=headers)
    
    print(f"[MCP tools] list_candidates status: {r.status_code}")
    print(f"[MCP tools] list_candidates response: {r.text}")
    if r.status_code == 200:
        data = r.json()
        
        # If all_candidates is True and there's pagination, fetch all pages
        if all_candidates and 'next' in data and data['next']:
            all_candidates_list = data.get('results', [])
            next_url = data['next']
            
            # Keep fetching until no more pages
            while next_url:
                print(f"[MCP tools] Fetching next page: {next_url}")
                r = requests.get(next_url, headers=headers)
                if r.status_code == 200:
                    page_data = r.json()
                    all_candidates_list.extend(page_data.get('results', []))
                    next_url = page_data.get('next')
                else:
                    break
            
            print(f"[MCP tools] Total candidates fetched: {len(all_candidates_list)}")
            return {
                "success": True,
                "results": all_candidates_list,
                "count": len(all_candidates_list),
                "all_pages": True
            }
        
        return data
    
    return {"success": False, "message": 'Failed to fetch candidates list.'}

def get_all_candidates(auth_token=None):
    """Get all candidates without pagination for vector search"""
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/all/'
    print(f"[MCP tools] get_all_candidates URL: {url}")
    print(f"[MCP tools] get_all_candidates headers: {headers}")
    
    r = requests.get(url, headers=headers)
    print(f"[MCP tools] get_all_candidates status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        candidates = data.get('candidates', [])
        count = data.get('count', len(candidates))
        print(f"[MCP tools] get_all_candidates found {count} candidates")
        return {"success": True, "candidates": candidates, "count": count}
    
    return {"success": False, "message": 'Failed to fetch all candidates.'}

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
    
    # Include Schema.org data if available
    schema_data = job_post.get('schema_org_data', {})
    schema_json = job_post.get('schema_org_json', '')
    
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
    
    # Add Schema.org structured data for AI understanding
    if schema_data:
        md += f"\n**Structured Data (Schema.org):**\n"
        md += f"```json\n{schema_json}\n```\n"
    
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
    
    # Include Schema.org data if available
    schema_data = candidate.get('schema_org_data', {})
    schema_json = candidate.get('schema_org_json', '')
    
    formatted_output = f"""
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
    
    # Add Schema.org structured data for AI understanding
    if schema_data:
        formatted_output += f"""
**Structured Data (Schema.org):**
```json
{schema_json}
```
"""
    
    return formatted_output

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
    
    # Add Schema.org context for AI understanding
    md += f"""
**Schema.org Context:**
This data represents job candidates with structured information including:
- Person schema with job application context
- Employment history and skills
- Geographic and contact information
- Application status and timeline
"""
    
    return md

def search_candidates(filters=None, auth_token=None):
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/'
    
    # Ensure params is a dictionary
    if isinstance(filters, dict):
        params = filters.copy()
    else:
        params = {}
    
    # Optimize search parameters
    search_query = None
    if isinstance(filters, dict):
        if 'search' in filters and filters['search']:
            search_query = filters['search']
            # Use search parameter for efficient database-level filtering
            params['search'] = search_query
            params['page_size'] = 100  # Reasonable page size
        elif 'name' in filters and filters['name']:
            search_query = filters['name']
            params['search'] = search_query
            params['page_size'] = 100
        else:
            params['page_size'] = 1000  # For other searches
    
    print(f"[MCP tools] Search: Using filters: {params}")
    print(f"[MCP tools] Search: Search query: {search_query}")
    r = requests.get(url, headers=headers, params=params)
    print(f"[MCP tools] Search: URL: {r.url}")
    print(f"[MCP tools] Search: Status: {r.status_code}")
    
    if r.status_code == 200:
        response_data = r.json()
        
        # Handle pagination efficiently
        if isinstance(response_data, dict) and 'results' in response_data:
            candidates = response_data['results']
            next_url = response_data.get('next')
            
            # For search queries, fetch additional pages if needed (but limit to reasonable amount)
            if search_query and next_url:
                page_count = 1
                max_pages = 5  # Limit to 5 pages for search queries
                
                while next_url and page_count < max_pages:
                    print(f"[MCP tools] Search: Fetching page {page_count + 1}: {next_url}")
                    r = requests.get(next_url, headers=headers)
                    if r.status_code == 200:
                        page_data = r.json()
                        candidates.extend(page_data.get('results', []))
                        next_url = page_data.get('next')
                        page_count += 1
                    else:
                        break
                
                if page_count >= max_pages:
                    print(f"[MCP tools] Search: Reached max pages limit ({max_pages})")
            elif not search_query:
                # For "all candidates" requests, limit to first page
                print(f"[MCP tools] Search: Limited to first page for 'all candidates' request")
            
            print(f"[MCP tools] Search: Total candidates found: {len(candidates)}")
        else:
            candidates = response_data
        
        return {"success": True, "candidates": candidates, "count": len(candidates)}
    
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

def search_candidate_by_name(name, auth_token=None):
    """Efficient search for candidate by name"""
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/'
    
    # Use search parameter for name search
    params = {'search': name, 'page_size': 100}  # Increased for better coverage
    
    print(f"[MCP tools] Name search: Looking for '{name}'")
    r = requests.get(url, headers=headers, params=params)
    print(f"[MCP tools] Name search URL: {r.url}")
    
    if r.status_code == 200:
        response_data = r.json()
        candidates = response_data.get('results', [])
        
        # Filter for exact name matches
        exact_matches = []
        partial_matches = []
        
        for candidate in candidates:
            candidate_name = candidate.get('name', '').lower()
            search_name = name.lower()
            
            if search_name in candidate_name or candidate_name in search_name:
                if candidate_name == search_name:
                    exact_matches.append(candidate)
                else:
                    partial_matches.append(candidate)
        
        # Return exact matches first, then partial matches
        all_matches = exact_matches + partial_matches
        
        if all_matches:
            return {"success": True, "candidates": all_matches, "count": len(all_matches)}
        else:
            return {"success": False, "message": f"No candidates found with name '{name}'"}
    
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    return {"success": False, "message": f"Failed to search for candidate '{name}'. Reason: {detail}"}

def vector_search_candidates(query, auth_token=None, limit=20):
    """Perform vector search on candidates using the Django backend"""
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    
    # Call the Django backend's vector search endpoint
    url = f'{DJANGO_API}/nlweb/vector/search/'
    payload = {
        "query": query,
        "search_type": "semantic",
        "limit": limit,
        "score_threshold": 0.7
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"[MCP tools] vector_search_candidates status: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            if result.get('success'):
                candidates = result.get('candidates', [])
                return {
                    "success": True,
                    "candidates": candidates,
                    "total_found": len(candidates),
                    "search_type": "vector_semantic"
                }
            else:
                return {"success": False, "message": result.get('message', 'Vector search failed')}
        else:
            return {"success": False, "message": f"Vector search failed with status {r.status_code}"}
    except Exception as e:
        print(f"[MCP tools] vector_search_candidates error: {e}")
        return {"success": False, "message": f"Vector search error: {str(e)}"}

def map_string_to_foreign_key(value, field_type, auth_token=None):
    """Map string values to foreign key IDs for the Django backend"""
    print(f"[MCP tools] map_string_to_foreign_key called with value: '{value}', field_type: '{field_type}'")
    
    if not value or value == '' or value.lower() in ['n/a', 'na', 'none', 'null']:
        print(f"[MCP tools] Value is empty or null, returning None")
        return None
    
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    
    # Define the mapping endpoints
    endpoints = {
        'job_title': f'{DJANGO_API}/jobtitles/',
        'city': f'{DJANGO_API}/cities/',
        'source': f'{DJANGO_API}/sources/',
        'communication_skills': f'{DJANGO_API}/communicationskills/'
    }
    
    if field_type not in endpoints:
        print(f"[MCP tools] Field type '{field_type}' not in endpoints, returning value as-is")
        return value  # Return as-is if not a foreign key field
    
    try:
        endpoint = endpoints[field_type]
        print(f"[MCP tools] Getting options from: {endpoint}")
        
        # Get all available options for this field type
        r = requests.get(endpoint, headers=headers)
        print(f"[MCP tools] GET request status: {r.status_code}")
        
        if r.status_code == 200:
            options = r.json()
            print(f"[MCP tools] Found {len(options)} options for {field_type}")
            print(f"[MCP tools] Trying to match value: '{value}'")
            print(f"[MCP tools] Available options: {[opt.get('name') for opt in options[:5]]}...")
            
            # Try exact match first (case insensitive)
            for option in options:
                if option.get('name', '').lower().strip() == value.lower().strip():
                    print(f"[MCP tools] Found exact match: {option.get('name')} -> {option.get('id')}")
                    return option.get('id')
            
            # Try partial match (case insensitive)
            for option in options:
                if value.lower().strip() in option.get('name', '').lower().strip():
                    print(f"[MCP tools] Found partial match: {option.get('name')} -> {option.get('id')}")
                    return option.get('id')
            
            # Try reverse partial match (option name in value)
            for option in options:
                if option.get('name', '').lower().strip() in value.lower().strip():
                    print(f"[MCP tools] Found reverse partial match: {option.get('name')} -> {option.get('id')}")
                    return option.get('id')
            
            print(f"[MCP tools] No match found for '{value}', creating new option")
            
            # If no match found, create the option (for job_titles, cities, sources, communication_skills)
            if field_type in ['job_title', 'city', 'source', 'communication_skills']:
                create_r = requests.post(endpoint, json={'name': value}, headers=headers)
                print(f"[MCP tools] CREATE request status: {create_r.status_code}")
                if create_r.status_code in (200, 201):
                    new_option = create_r.json()
                    print(f"[MCP tools] Created new option: {new_option.get('name')} -> {new_option.get('id')}")
                    return new_option.get('id')
                else:
                    print(f"[MCP tools] Failed to create option: {create_r.text}")
        
        print(f"[MCP tools] Returning None for '{value}'")
        return None
    except Exception as e:
        print(f"[MCP tools] Error mapping {field_type} '{value}': {e}")
        return None

def convert_candidate_data(candidate_data):
    """Convert candidate data from CSV format to Django API format"""
    converted = {}
    
    # Direct field mappings
    direct_fields = ['first_name', 'last_name', 'email', 'phone_number', 'candidate_stage', 'notes']
    for field in direct_fields:
        if field in candidate_data:
            converted[field] = candidate_data[field]
    
    # Numeric fields
    numeric_fields = ['years_of_experience', 'expected_salary', 'current_salary']
    for field in numeric_fields:
        if field in candidate_data:
            try:
                value = candidate_data[field]
                if isinstance(value, str):
                    value = value.replace(',', '').strip()
                converted[field] = float(value) if value else 0.0
            except (ValueError, TypeError):
                converted[field] = 0.0
    
    # Foreign key fields - these will be handled by the mapping function
    fk_fields = ['job_title', 'city', 'source', 'communication_skills']
    for field in fk_fields:
        if field in candidate_data:
            converted[field] = candidate_data[field]  # Keep as string for now
    
    return converted

def bulk_add_candidates(candidates, auth_token=None):
    """Add multiple candidates to the system with proper data conversion"""
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/candidates/'
    
    results = []
    added_count = 0
    skipped_count = 0
    
    print(f"[MCP tools] bulk_add_candidates: Processing {len(candidates)} candidates")
    
    try:
        for i, candidate_data in enumerate(candidates):
            try:
                print(f"[MCP tools] Processing candidate {i+1}/{len(candidates)}: {candidate_data.get('first_name', 'Unknown')} {candidate_data.get('last_name', '')}")
                
                # Convert the data format
                converted_data = convert_candidate_data(candidate_data)
                
                # Map foreign key fields
                fk_fields = ['job_title', 'city', 'source', 'communication_skills']
                for field in fk_fields:
                    if field in converted_data and converted_data[field]:
                        fk_id = map_string_to_foreign_key(converted_data[field], field, auth_token)
                        if fk_id is not None:
                            converted_data[field] = fk_id
                        else:
                            # If mapping failed, try to create a default value for required fields
                            if field in ['job_title', 'communication_skills']:
                                # Create a default entry for required fields
                                try:
                                    default_value = "General" if field == "job_title" else "Good"
                                    create_r = requests.post(
                                        f'{DJANGO_API}/{"jobtitles" if field == "job_title" else "communicationskills"}/',
                                        json={'name': default_value},
                                        headers=headers
                                    )
                                    if create_r.status_code in (200, 201):
                                        new_option = create_r.json()
                                        converted_data[field] = new_option.get('id')
                                        print(f"[MCP tools] Created default {field}: {default_value}")
                                    else:
                                        print(f"[MCP tools] Warning: Could not create default {field}")
                                except Exception as e:
                                    print(f"[MCP tools] Error creating default {field}: {e}")
                            # Keep the original string value if mapping fails - don't delete the field
                            print(f"[MCP tools] Warning: Could not map {field} '{converted_data.get(field, 'N/A')}' for candidate {i+1}, keeping original value")
                
                print(f"[MCP tools] Converted data for candidate {i+1}: {converted_data}")
                print(f"[MCP tools] Sending request to: {url}")
                print(f"[MCP tools] Headers: {headers}")
                
                try:
                    r = requests.post(url, json=converted_data, headers=headers)
                    print(f"[MCP tools] Response status for candidate {i+1}: {r.status_code}")
                    print(f"[MCP tools] Response text: {r.text}")
                    
                    if r.status_code in (200, 201):
                        results.append({"success": True, "candidate": r.json()})
                        added_count += 1
                        print(f"[MCP tools] ✅ Successfully added candidate {i+1}")
                    else:
                        try:
                            err = r.json()
                            detail = err.get('detail') or err.get('message') or str(err)
                            print(f"[MCP tools] ❌ Error for candidate {i+1}: {detail}")
                        except Exception:
                            detail = r.text
                            print(f"[MCP tools] ❌ Error for candidate {i+1}: {detail}")
                        
                        # Check if it's a duplicate error
                        if 'already exists' in detail.lower() or 'duplicate' in detail.lower():
                            skipped_count += 1
                            print(f"[MCP tools] ⚠️ Skipped duplicate candidate {i+1}")
                        
                        results.append({"success": False, "message": detail})
                except Exception as e:
                    error_msg = f"Error adding candidate {i+1}: {str(e)}"
                    print(f"[MCP tools] ❌ {error_msg}")
                    results.append({"success": False, "message": error_msg})
            except Exception as e:
                error_msg = f"Error processing candidate {i+1}: {str(e)}"
                print(f"[MCP tools] ❌ {error_msg}")
                results.append({"success": False, "message": error_msg})
    except Exception as e:
        print(f"[MCP tools] ❌ Error in bulk_add_candidates: {str(e)}")
        results.append({"success": False, "message": f"Bulk operation failed: {str(e)}"})
    
    # Return a dictionary with summary information
    summary = {
        "success": added_count > 0,
        "added_count": added_count,
        "skipped_count": skipped_count,
        "failed_count": len(results) - added_count - skipped_count,
        "total_processed": len(results),
        "results": results,
        "message": f"Processed {len(results)} candidates: {added_count} added, {skipped_count} skipped, {len(results) - added_count - skipped_count} failed"
    }
    
    print(f"[MCP tools] Bulk add summary: {summary}")
    return summary

def get_schema_org_data(data_type='candidates', candidate_id=None, job_post_id=None, auth_token=None):
    """
    Fetch Schema.org structured data for better AI understanding.
    
    Args:
        data_type: 'candidates' or 'job_posts'
        candidate_id: Specific candidate ID (optional)
        job_post_id: Specific job post ID (optional)
        auth_token: Authentication token
    
    Returns:
        Schema.org structured data in JSON format
    """
    headers = {"Authorization": f"Token {auth_token}"} if auth_token else {}
    url = f'{DJANGO_API}/schema-org-data/'
    
    params = {'type': data_type}
    if candidate_id:
        params['candidate_id'] = candidate_id
    if job_post_id:
        params['job_post_id'] = job_post_id
    
    print(f"[MCP tools] get_schema_org_data URL: {url}")
    print(f"[MCP tools] get_schema_org_data params: {params}")
    print(f"[MCP tools] get_schema_org_data headers: {headers}")
    
    r = requests.get(url, params=params, headers=headers)
    print(f"[MCP tools] get_schema_org_data status: {r.status_code}")
    print(f"[MCP tools] get_schema_org_data response: {r.text}")
    
    if r.status_code == 200:
        response_data = r.json()
        return {
            "success": True,
            "schema_data": response_data.get('data'),
            "type": response_data.get('type'),
            "context": response_data.get('context'),
            "count": response_data.get('count', 1)
        }
    
    try:
        err = r.json()
        detail = err.get('detail') or err.get('message') or str(err)
    except Exception:
        detail = r.text
    
    return {
        "success": False, 
        "message": f"Failed to fetch Schema.org data. Reason: {detail}"
    } 