#!/usr/bin/env python3
"""
Add Sample Data to Vector Database
This script adds sample candidates and job posts to test vector search functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_sample_candidates():
    """Add sample candidates to the vector database"""
    
    print("👥 Adding sample candidates...")
    
    sample_candidates = [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0123",
            "experience_years": 5,
            "skills": ["Python", "Django", "React", "JavaScript", "SQL", "AWS"],
            "current_position": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "salary_expectation": 120000,
            "education": "Bachelor's in Computer Science",
            "resume_summary": "Experienced software engineer with 5 years of experience in full-stack development. Proficient in Python, Django, React, and cloud technologies. Led multiple successful projects and mentored junior developers."
        },
        {
            "id": 2,
            "name": "Sarah Johnson",
            "email": "sarah.johnson@email.com",
            "phone": "+1-555-0124",
            "experience_years": 3,
            "skills": ["Java", "Spring Boot", "Microservices", "Docker", "Kubernetes"],
            "current_position": "Backend Developer",
            "location": "New York, NY",
            "salary_expectation": 95000,
            "education": "Master's in Software Engineering",
            "resume_summary": "Backend developer specializing in Java and microservices architecture. Experience with Spring Boot, Docker, and Kubernetes. Strong problem-solving skills and team collaboration."
        },
        {
            "id": 3,
            "name": "Michael Chen",
            "email": "michael.chen@email.com",
            "phone": "+1-555-0125",
            "experience_years": 7,
            "skills": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Data Analysis"],
            "current_position": "Data Scientist",
            "location": "Seattle, WA",
            "salary_expectation": 140000,
            "education": "PhD in Computer Science",
            "resume_summary": "Senior data scientist with expertise in machine learning and AI. Published research in top conferences. Experience with Python, TensorFlow, PyTorch, and big data technologies."
        },
        {
            "id": 4,
            "name": "Emily Rodriguez",
            "email": "emily.rodriguez@email.com",
            "phone": "+1-555-0126",
            "experience_years": 2,
            "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Git"],
            "current_position": "Frontend Developer",
            "location": "Austin, TX",
            "salary_expectation": 75000,
            "education": "Bachelor's in Web Development",
            "resume_summary": "Frontend developer passionate about creating user-friendly web applications. Proficient in React, JavaScript, and modern web technologies. Strong attention to detail and user experience."
        },
        {
            "id": 5,
            "name": "David Kim",
            "email": "david.kim@email.com",
            "phone": "+1-555-0127",
            "experience_years": 4,
            "skills": ["C#", ".NET", "Azure", "SQL Server", "DevOps"],
            "current_position": "Full Stack Developer",
            "location": "Chicago, IL",
            "salary_expectation": 110000,
            "education": "Bachelor's in Information Technology",
            "resume_summary": "Full stack developer with expertise in Microsoft technologies. Experience with C#, .NET, Azure cloud services, and DevOps practices. Strong problem-solving and communication skills."
        }
    ]
    
    try:
        from vector_db import vector_db
        
        indexed_count = 0
        for candidate in sample_candidates:
            success = vector_db.index_candidate(candidate)
            if success:
                indexed_count += 1
                print(f"✅ Indexed: {candidate['name']} - {candidate['current_position']}")
            else:
                print(f"❌ Failed to index: {candidate['name']}")
        
        print(f"\n📊 Successfully indexed {indexed_count}/{len(sample_candidates)} candidates")
        return True
        
    except Exception as e:
        print(f"❌ Error indexing candidates: {e}")
        return False

def add_sample_jobs():
    """Add sample job posts to the vector database"""
    
    print("\n💼 Adding sample job posts...")
    
    sample_jobs = [
        {
            "id": 1,
            "title": "Senior Software Engineer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA",
            "salary_range": "120000-150000",
            "experience_required": "5+ years",
            "skills_required": ["Python", "Django", "React", "AWS", "SQL"],
            "job_description": "We're looking for a Senior Software Engineer to join our growing team. You'll be responsible for developing and maintaining web applications using Python, Django, and React. Experience with cloud technologies and databases required.",
            "job_type": "Full-time",
            "remote_option": "Hybrid"
        },
        {
            "id": 2,
            "title": "Data Scientist",
            "company": "DataFlow Analytics",
            "location": "Seattle, WA",
            "salary_range": "130000-160000",
            "experience_required": "3+ years",
            "skills_required": ["Python", "Machine Learning", "TensorFlow", "SQL", "Statistics"],
            "job_description": "Join our data science team to build machine learning models and analyze large datasets. Experience with Python, TensorFlow, and statistical analysis required. PhD preferred but not required.",
            "job_type": "Full-time",
            "remote_option": "Remote"
        },
        {
            "id": 3,
            "title": "Frontend Developer",
            "company": "WebSolutions Ltd.",
            "location": "Austin, TX",
            "salary_range": "80000-100000",
            "experience_required": "2+ years",
            "skills_required": ["JavaScript", "React", "CSS", "HTML", "Git"],
            "job_description": "We're seeking a Frontend Developer to create beautiful and responsive user interfaces. Experience with React, JavaScript, and modern web technologies required. Strong design sense and attention to detail.",
            "job_type": "Full-time",
            "remote_option": "On-site"
        },
        {
            "id": 4,
            "title": "DevOps Engineer",
            "company": "CloudTech Systems",
            "location": "New York, NY",
            "salary_range": "110000-140000",
            "experience_required": "4+ years",
            "skills_required": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
            "job_description": "Join our DevOps team to manage cloud infrastructure and deployment pipelines. Experience with Docker, Kubernetes, AWS, and CI/CD tools required. Strong automation and scripting skills.",
            "job_type": "Full-time",
            "remote_option": "Hybrid"
        },
        {
            "id": 5,
            "title": "Backend Developer",
            "company": "API Solutions",
            "location": "Chicago, IL",
            "salary_range": "90000-120000",
            "experience_required": "3+ years",
            "skills_required": ["Java", "Spring Boot", "Microservices", "SQL", "REST APIs"],
            "job_description": "We're looking for a Backend Developer to build scalable microservices and APIs. Experience with Java, Spring Boot, and database design required. Knowledge of cloud platforms preferred.",
            "job_type": "Full-time",
            "remote_option": "Remote"
        }
    ]
    
    try:
        from vector_db import vector_db
        
        indexed_count = 0
        for job in sample_jobs:
            success = vector_db.index_job_post(job)
            if success:
                indexed_count += 1
                print(f"✅ Indexed: {job['title']} at {job['company']}")
            else:
                print(f"❌ Failed to index: {job['title']}")
        
        print(f"\n📊 Successfully indexed {indexed_count}/{len(sample_jobs)} job posts")
        return True
        
    except Exception as e:
        print(f"❌ Error indexing jobs: {e}")
        return False

def test_vector_search():
    """Test vector search with sample data"""
    
    print("\n🔍 Testing vector search functionality...")
    
    try:
        from vector_db import vector_db
        
        # Test queries
        test_queries = [
            "Python developers",
            "Machine learning engineers",
            "Frontend developers with React experience",
            "Senior software engineers in San Francisco",
            "Data scientists with Python skills",
            "Backend developers with Java experience"
        ]
        
        for query in test_queries:
            print(f"\n🔎 Query: '{query}'")
            
            # Search candidates
            candidates = vector_db.search_candidates(query, limit=3, score_threshold=0.5)
            print(f"  Candidates found: {len(candidates)}")
            for candidate in candidates[:2]:  # Show top 2
                print(f"    - {candidate.get('name', 'Unknown')}: {candidate.get('current_position', 'Unknown')}")
            
            # Search jobs
            jobs = vector_db.search_job_posts(query, limit=3, score_threshold=0.5)
            print(f"  Jobs found: {len(jobs)}")
            for job in jobs[:2]:  # Show top 2
                print(f"    - {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing vector search: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Adding Sample Data to Vector Database")
    print("=" * 50)
    
    # Add sample candidates
    candidates_ok = add_sample_candidates()
    
    # Add sample jobs
    jobs_ok = add_sample_jobs()
    
    if candidates_ok and jobs_ok:
        print("\n✅ Sample data added successfully!")
        
        # Test vector search
        test_vector_search()
        
        print("\n🎉 Vector database is now ready for testing!")
        print("\n💡 Next steps:")
        print("1. Test vector search: python tests/test_vector_nlweb.py")
        print("2. Try semantic queries through the API")
        print("3. Integrate with your frontend application")
    else:
        print("\n❌ Failed to add sample data. Please check your configuration.") 