import streamlit as st
import os
import io
import zipfile
from utils.cloud import upload_to_r2

st.header("📁 フォルダ自動ファイル整理 (Auto File Organizer)")
st.write("ファイルをドラッグ＆ドロップして、拡張子ごとに自動仕分けを行います。")

uploaded_files = st.file_uploader("仕分けたいファイルをまとめて選択", accept_multiple_files=True, key="organizer_files")

if st.button("🚀 ファイル自動仕分けを実行", type="primary", use_container_width=True):
    if uploaded_files:
        zip_buf = io.BytesIO()
        folder_map = {
            ".pdf": "PDF_Documents",
            ".jpg": "Images", ".png": "Images", ".jpeg": "Images",
            ".xlsx": "Excel_Spreadsheets",
            ".docx": "Word_Documents",
            ".zip": "Archives",
            ".mp4": "Video_Files",
            ".wav": "Audio_Files"
        }

        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in uploaded_files:
                ext = os.path.splitext(f.name)[1].lower()
                folder_name = folder_map.get(ext, "Others")
                zf.writestr(f"{folder_name}/{f.name}", f.getvalue())

        st.success("✨ すべてのファイルの仕分けが完了しました！")
        
        # ZIPダウンロード
        st.download_button(
            label="📦 仕分け済みフォルダをZIPで一括ダウンロード",
            data=zip_buf.getvalue(),
            file_name="organized_files.zip",
            mime="application/zip"
        )

        # ProならR2へ保存
        is_pro = st.session_state.get("is_pro", False)
        if is_pro:
            r2_url = upload_to_r2(zip_buf.getvalue(), "organized_files.zip")
            if r2_url:
                st.success("☁️ Cloudflare R2 クラウドストレージに安全に保存されました！")
                st.markdown(f"🔗 **[クラウドから一括ダウンロード（有効期限: 1時間）]({r2_url})**")
        else:
            st.info("🔒 Cloudflare R2 クラウドへの自動保存機能は Pro プラン限定です。")
    else:
        st.warning("ファイルを選択してください。")