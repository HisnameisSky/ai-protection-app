import streamlit as st
from supabase import create_client
import resend
import datetime

@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def verify_pro_key(user_key: str) -> bool:
    if not user_key:
        return False
    try:
        supabase = init_supabase()
        response = supabase.table("license_keys").select("*").eq("key_code", user_key).eq("is_active", True).execute()
        return len(response.data) > 0
    except Exception:
        return False