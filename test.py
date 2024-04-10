from supabase import create_client, Client
import os 
from dotenv import load_dotenv

load_dotenv()


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

picturedata = supabase.storage.from_("pictures").list()
print(picturedata)