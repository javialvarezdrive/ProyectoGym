# utils/database.py
from supabase import create_client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
