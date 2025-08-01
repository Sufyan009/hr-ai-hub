import os
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models as rest
import openai
from dotenv import load_dotenv

load_dotenv()

class HRVectorDatabase:
    """
    Vector database for HR Assistant Pro using Qdrant and Azure OpenAI embeddings.
    Enables semantic search of candidates, job posts, and other HR data.
    """
    
    def __init__(self):
        self.qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        self.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_openai_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'text-embedding-ada-002')
        
        # Initialize clients
        self.qdrant_client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )
        
        # Initialize Azure OpenAI client
        self.azure_client = openai.AzureOpenAI(
            azure_endpoint=self.azure_openai_endpoint,
            api_key=self.azure_openai_api_key,
            api_version="2023-05-15"
        )
        
        # Collection names
        self.collections = {
            'candidates': 'hr_candidates',
            'job_posts': 'hr_job_posts',
            'analytics': 'hr_analytics'
        }
        
        # Initialize collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize Qdrant collections with proper schema"""
        for collection_name in self.collections.values():
            try:
                # Check if collection exists
                collections = self.qdrant_client.get_collections()
                exists = any(col.name == collection_name for col in collections.collections)
                
                if not exists:
                    # Create collection with 1536 dimensions (Ada-002 embedding size)
                    self.qdrant_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                        optimizers_config={
                            "default_segment_number": 2,
                        }
                    )
                    print(f"✅ Created collection: {collection_name}")
                else:
                    print(f"✅ Collection exists: {collection_name}")
                    
            except Exception as e:
                print(f"⚠️ Error initializing collection {collection_name}: {e}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from Azure OpenAI Ada-002 model"""
        try:
            response = self.azure_client.embeddings.create(
                input=text,
                model=self.azure_openai_deployment
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Error getting embedding: {e}")
            return []
    
    def _prepare_candidate_text(self, candidate: Dict[str, Any]) -> str:
        """Prepare candidate data for embedding"""
        text_parts = [
            f"Name: {candidate.get('first_name', '')} {candidate.get('last_name', '')}",
            f"Email: {candidate.get('email', '')}",
            f"Phone: {candidate.get('phone_number', '')}",
            f"Job Title: {candidate.get('job_title_detail', {}).get('title', '') if candidate.get('job_title_detail') else ''}",
            f"City: {candidate.get('city_detail', {}).get('name', '') if candidate.get('city_detail') else ''}",
            f"Stage: {candidate.get('candidate_stage', '')}",
            f"Current Salary: {candidate.get('current_salary', '')}",
            f"Expected Salary: {candidate.get('expected_salary', '')}",
            f"Experience: {candidate.get('years_of_experience', '')} years",
            f"Source: {candidate.get('source_detail', {}).get('name', '') if candidate.get('source_detail') else ''}",
            f"Skills: {candidate.get('communication_skills_detail', {}).get('skill', '') if candidate.get('communication_skills_detail') else ''}",
            f"Notes: {candidate.get('notes', '')}"
        ]
        return " | ".join(filter(None, text_parts))
    
    def _prepare_job_text(self, job: Dict[str, Any]) -> str:
        """Prepare job post data for embedding"""
        text_parts = [
            f"Title: {job.get('title', '')}",
            f"Company: {job.get('company', '')}",
            f"Location: {job.get('location', '')}",
            f"Description: {job.get('description', '')}",
            f"Requirements: {job.get('requirements', '')}",
            f"Salary Range: {job.get('min_salary', '')} - {job.get('max_salary', '')}",
            f"Status: {job.get('status', '')}"
        ]
        return " | ".join(filter(None, text_parts))
    
    def index_candidate(self, candidate: Dict[str, Any]) -> bool:
        """Index a candidate in the vector database"""
        try:
            # Prepare text for embedding
            text = self._prepare_candidate_text(candidate)
            if not text.strip():
                return False
            
            # Get embedding
            embedding = self._get_embedding(text)
            if not embedding:
                return False
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'id': candidate.get('id'),
                    'type': 'candidate',
                    'name': f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}",
                    'email': candidate.get('email', ''),
                    'job_title': candidate.get('job_title_detail', {}).get('title', '') if candidate.get('job_title_detail') else '',
                    'stage': candidate.get('candidate_stage', ''),
                    'salary': candidate.get('current_salary', ''),
                    'experience': candidate.get('years_of_experience', ''),
                    'city': candidate.get('city_detail', {}).get('name', '') if candidate.get('city_detail') else '',
                    'source': candidate.get('source_detail', {}).get('name', '') if candidate.get('source_detail') else '',
                    'skills': candidate.get('communication_skills_detail', {}).get('skill', '') if candidate.get('communication_skills_detail') else '',
                    'notes': candidate.get('notes', ''),
                    'created_at': candidate.get('created_at', ''),
                    'text': text,
                    'schema_org_data': candidate.get('schema_org_data', {}),
                    'schema_org_json': candidate.get('schema_org_json', '')
                }
            )
            
            # Upsert to collection
            self.qdrant_client.upsert(
                collection_name=self.collections['candidates'],
                points=[point]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error indexing candidate: {e}")
            return False
    
    def index_job_post(self, job: Dict[str, Any]) -> bool:
        """Index a job post in the vector database"""
        try:
            # Prepare text for embedding
            text = self._prepare_job_text(job)
            if not text.strip():
                return False
            
            # Get embedding
            embedding = self._get_embedding(text)
            if not embedding:
                return False
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'id': job.get('id'),
                    'type': 'job_post',
                    'title': job.get('title', ''),
                    'company': job.get('company', ''),
                    'location': job.get('location', ''),
                    'description': job.get('description', ''),
                    'requirements': job.get('requirements', ''),
                    'min_salary': job.get('min_salary', ''),
                    'max_salary': job.get('max_salary', ''),
                    'status': job.get('status', ''),
                    'created_at': job.get('created_at', ''),
                    'text': text,
                    'schema_org_data': job.get('schema_org_data', {}),
                    'schema_org_json': job.get('schema_org_json', '')
                }
            )
            
            # Upsert to collection
            self.qdrant_client.upsert(
                collection_name=self.collections['job_posts'],
                points=[point]
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error indexing job post: {e}")
            return False
    
    def search_candidates(self, query: str, limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search candidates using semantic similarity"""
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return []
            
            # Search in candidates collection
            search_result = self.qdrant_client.search(
                collection_name=self.collections['candidates'],
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )
            
            results = []
            for point in search_result:
                results.append({
                    'id': point.payload.get('id'),
                    'name': point.payload.get('name'),
                    'email': point.payload.get('email'),
                    'job_title': point.payload.get('job_title'),
                    'stage': point.payload.get('stage'),
                    'salary': point.payload.get('salary'),
                    'experience': point.payload.get('experience'),
                    'city': point.payload.get('city'),
                    'source': point.payload.get('source'),
                    'skills': point.payload.get('skills'),
                    'notes': point.payload.get('notes'),
                    'score': point.score,
                    'schema_org_data': point.payload.get('schema_org_data'),
                    'schema_org_json': point.payload.get('schema_org_json')
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching candidates: {e}")
            return []
    
    def search_job_posts(self, query: str, limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search job posts using semantic similarity"""
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return []
            
            # Search in job posts collection
            search_result = self.qdrant_client.search(
                collection_name=self.collections['job_posts'],
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            )
            
            results = []
            for point in search_result:
                results.append({
                    'id': point.payload.get('id'),
                    'title': point.payload.get('title'),
                    'company': point.payload.get('company'),
                    'location': point.payload.get('location'),
                    'description': point.payload.get('description'),
                    'requirements': point.payload.get('requirements'),
                    'min_salary': point.payload.get('min_salary'),
                    'max_salary': point.payload.get('max_salary'),
                    'status': point.payload.get('status'),
                    'score': point.score,
                    'schema_org_data': point.payload.get('schema_org_data'),
                    'schema_org_json': point.payload.get('schema_org_json')
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching job posts: {e}")
            return []
    
    def search_all(self, query: str, limit: int = 20, score_threshold: float = 0.7) -> Dict[str, List[Dict[str, Any]]]:
        """Search both candidates and job posts"""
        candidates = self.search_candidates(query, limit // 2, score_threshold)
        job_posts = self.search_job_posts(query, limit // 2, score_threshold)
        
        return {
            'candidates': candidates,
            'job_posts': job_posts,
            'total_results': len(candidates) + len(job_posts)
        }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collections"""
        try:
            stats = {}
            for name, collection in self.collections.items():
                try:
                    collection_info = self.qdrant_client.get_collection(collection)
                    stats[name] = {
                        'name': collection,
                        'points_count': collection_info.points_count,
                        'vectors_count': collection_info.vectors_count,
                        'status': collection_info.status
                    }
                except Exception as e:
                    stats[name] = {'error': str(e)}
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def clear_collection(self, collection_type: str):
        """Clear a specific collection"""
        try:
            if collection_type in self.collections:
                self.qdrant_client.delete_collection(self.collections[collection_type])
                self._init_collections()
                print(f"✅ Cleared collection: {self.collections[collection_type]}")
        except Exception as e:
            print(f"❌ Error clearing collection: {e}")

# Global instance
vector_db = HRVectorDatabase() 