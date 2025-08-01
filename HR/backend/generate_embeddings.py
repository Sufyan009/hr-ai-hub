#!/usr/bin/env python3
"""
Generate Embeddings Script
Indexes all existing candidates and job posts into Qdrant vector database
"""

import os
import sys
import django
from dotenv import load_dotenv

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import Candidate, JobPost
from vector_db import HRVectorDatabase
import json

load_dotenv()

def index_all_candidates():
    """Index all candidates into vector database"""
    print("👥 Indexing all candidates...")
    
    try:
        vector_db = HRVectorDatabase()
        candidates = Candidate.objects.all()
        
        print(f"Found {candidates.count()} candidates to index")
        
        success_count = 0
        error_count = 0
        
        for candidate in candidates:
            try:
                # Convert Django model to dict with correct field names
                candidate_data = {
                    'id': candidate.id,
                    'first_name': candidate.first_name,
                    'last_name': candidate.last_name,
                    'email': candidate.email,
                    'phone_number': candidate.phone_number,
                    'candidate_stage': candidate.candidate_stage,
                    'current_salary': str(candidate.current_salary) if candidate.current_salary else '',
                    'expected_salary': str(candidate.expected_salary) if candidate.expected_salary else '',
                    'years_of_experience': str(candidate.years_of_experience) if candidate.years_of_experience else '',
                    'job_title_detail': {'title': candidate.job_title.name if candidate.job_title else ''},
                    'city_detail': {'name': candidate.city.name if candidate.city else ''},
                    'source_detail': {'name': candidate.source.name if candidate.source else ''},
                    'communication_skills_detail': {'skill': candidate.communication_skills.name if candidate.communication_skills else ''}
                }
                
                # Index the candidate
                success = vector_db.index_candidate(candidate_data)
                
                if success:
                    success_count += 1
                    print(f"✅ Indexed candidate: {candidate.first_name} {candidate.last_name}")
                else:
                    error_count += 1
                    print(f"❌ Failed to index candidate: {candidate.first_name} {candidate.last_name}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error indexing candidate {candidate.id}: {e}")
        
        print(f"\n📊 Candidate Indexing Results:")
        print(f"   ✅ Successfully indexed: {success_count}")
        print(f"   ❌ Failed to index: {error_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error in candidate indexing: {e}")
        return False

def index_all_job_posts():
    """Index all job posts into vector database"""
    print("\n💼 Indexing all job posts...")
    
    try:
        vector_db = HRVectorDatabase()
        job_posts = JobPost.objects.all()
        
        print(f"Found {job_posts.count()} job posts to index")
        
        success_count = 0
        error_count = 0
        
        for job_post in job_posts:
            try:
                # Convert Django model to dict with correct field names
                job_data = {
                    'id': job_post.id,
                    'title': job_post.title,
                    'description': job_post.description,
                    'requirements': job_post.requirements,
                    'salary_min': str(job_post.salary_min) if job_post.salary_min else '',
                    'salary_max': str(job_post.salary_max) if job_post.salary_max else '',
                    'location': job_post.location,
                    'job_type': job_post.employment_type,  # Use employment_type instead of job_type
                    'experience_level': '',  # Not in model, use empty string
                    'status': job_post.status
                }
                
                # Index the job post
                success = vector_db.index_job_post(job_data)
                
                if success:
                    success_count += 1
                    print(f"✅ Indexed job post: {job_post.title}")
                else:
                    error_count += 1
                    print(f"❌ Failed to index job post: {job_post.title}")
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error indexing job post {job_post.id}: {e}")
        
        print(f"\n📊 Job Post Indexing Results:")
        print(f"   ✅ Successfully indexed: {success_count}")
        print(f"   ❌ Failed to index: {error_count}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error in job post indexing: {e}")
        return False

def check_indexing_results():
    """Check the results of indexing"""
    print("\n🔍 Checking indexing results...")
    
    try:
        vector_db = HRVectorDatabase()
        
        # Check collections
        client = vector_db.qdrant_client
        
        for collection_name in ['hr_candidates', 'hr_job_posts']:
            try:
                collection_info = client.get_collection(collection_name)
                print(f"📋 {collection_name}: {collection_info.points_count} points")
            except Exception as e:
                print(f"❌ Error checking {collection_name}: {e}")
                
    except Exception as e:
        print(f"❌ Error checking results: {e}")

def main():
    """Main function to generate embeddings"""
    print("🚀 HR Assistant Pro - Generate Embeddings")
    print("=" * 50)
    
    # Check if vector database is configured
    try:
        vector_db = HRVectorDatabase()
        print("✅ Vector database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize vector database: {e}")
        print("Please check your .env file for QDRANT_URL and AZURE_OPENAI settings")
        return
    
    # Index all candidates
    candidates_success = index_all_candidates()
    
    # Index all job posts
    job_posts_success = index_all_job_posts()
    
    # Check results
    check_indexing_results()
    
    print("\n🎉 Embedding Generation Complete!")
    if candidates_success or job_posts_success:
        print("✅ Successfully generated embeddings for your data!")
        print("You can now use vector search in your NLWeb interface.")
    else:
        print("❌ No embeddings were generated. Check your configuration.")

if __name__ == "__main__":
    main() 