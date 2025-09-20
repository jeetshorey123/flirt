import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """Create and return a Supabase client"""
    url = os.environ.get('REACT_APP_SUPABASE_URL')
    key = os.environ.get('REACT_APP_SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError("Supabase URL and ANON KEY must be set in environment variables")
    
    supabase: Client = create_client(url, key)
    return supabase