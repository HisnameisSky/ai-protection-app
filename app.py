import streamlit as st
from utils.auth import verify_pro_key

st.set_page_config(page_title="AI Protection Pro Studio v7.0", page_icon="🛡️", layout="wide")

st.sidebar.subheader("🔑 Pro Plan Unlock")
user_key = st.sidebar.text_input("アクセスキーを入力", type="password", key="global_key")

# セッションにPro状態を保持
st.session_state["is_pro"] = verify_pro_key(user_key)

if st.session_state["is_pro"]:
    st.sidebar.success("🔓 Pro機能が解放されました！")
else:
    st.sidebar.warning("🔒 無料版モード")

st.title("🛡️ AI Protection Pro Studio v7.0")
st.write("左側のサイドバーから機能を選択してください。")
