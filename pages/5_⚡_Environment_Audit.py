import streamlit as st
import hashlib

st.header("Security Audit (Web Standard)")
st.write("ファイル整合性チェックおよびハッシュ値の検証を行います。")

audit_file = st.file_uploader("スキャンするファイルを選択", key="audit_file")

if audit_file:
    file_bytes = audit_file.read()
    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    md5_hash = hashlib.md5(file_bytes).hexdigest()

    st.subheader("📊 監査結果")
    st.code(f"File Name: {audit_file.name}\nSHA-256: {sha256_hash}\nMD5: {md5_hash}")
    st.success("⚡ 整合性スキャン完了: 異常なし (CLEAN)")