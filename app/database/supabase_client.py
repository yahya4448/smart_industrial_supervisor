import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_historical_incidents(machine_id: str):
    # Utilise directement le client supabase, c'est plus propre
    response = supabase.table("incidents").select("*").eq("machine_id", machine_id).execute()
    return response.data

def log_new_incident(data: dict):
    response = supabase.table("incidents").insert(data).execute()
    return response.data