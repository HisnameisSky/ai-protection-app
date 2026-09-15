import streamlit as st
import base64
from cryptography.fernet import Fernet
from utils.crypto import get_fernet_key

st.header("Document & Code Vault")
st.write("MS Word, Excel, PDF, Python(.py) などの任意ファイルを AES-256 で暗号化/復元します。")

doc_file = st.file_uploader("対象ファイルを選択", key="doc_file")
doc_pass = st.text_input("専用暗号化パスワード", type="password", key="doc_pass")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔒 ファイルを暗号化 (Lock)", type="primary", use_container_width=True):
        if doc_file and doc_pass:
            salt = b"static_salt_v7" # 固定ソルト（簡易版）
            key = get_fernet_key(doc_pass, salt)
            f = Fernet(key)
            encrypted_data = f.encrypt(doc_file.read())
            
            st.success("ファイルを暗号化しました！")
            st.download_button("⬇️ 暗号化ファイルをダウンロード", encrypted_data, file_name=f"{doc_file.name}.lock", mime="application/octet-stream")
        else:
            st.warning("ファイルとパスワードを指定してください。")

with col2:
    if st.button("🔓 ファイルを復元 (Unlock)", use_container_width=True):
        if doc_file and doc_pass:
            try:
                salt = b"static_salt_v7"
                key = get_fernet_key(doc_pass, salt)
                f = Fernet(key)
                decrypted_data = f.decrypt(doc_file.read())
                
                original_name = doc_file.name.replace(".lock", "")
                st.success("ファイルの復元に成功しました！")
                st.download_button("⬇️ 復元ファイルをダウンロード", decrypted_data, file_name=original_name, mime="application/octet-stream")
            except Exception:
                st.error("復元に失敗しました。パスワードが正しくないかファイルが破損しています。")
        else:
            st.warning("ファイルとパスワードを指定してください。")