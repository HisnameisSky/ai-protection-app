import streamlit as st
import pyzipper
import io

st.header("Secure ZIP Packager")
st.write("ファイルをAES-256で暗号化したパスワード付きZIPアーカイブを作成します。")

uploaded_files = st.file_uploader("圧縮するファイルを選択", accept_multiple_files=True, key="zip_files")
password = st.text_input("暗号化パスワード", type="password", key="zip_pass")

if st.button("🔒 強固なパスワード付きZIPを作成", type="primary", use_container_width=True):
    if uploaded_files and password:
        zip_buf = io.BytesIO()
        with pyzipper.AESZipFile(zip_buf, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WASM_AES_256) as zf:
            zf.setpassword(password.encode('utf-8'))
            for f in uploaded_files:
                zf.writestr(f.name, f.getvalue())
        
        st.success("ZIPアーカイブの作成が完了しました！")
        st.download_button(
            label="⬇️ 暗号化ZIPをダウンロード",
            data=zip_buf.getvalue(),
            file_name="secure_archive.zip",
            mime="application/zip"
        )
    else:
        st.warning("ファイルとパスワードの両方を入力してください。")