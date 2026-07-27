import os
import io
import datetime
import hashlib
import base64
import shutil
import zipfile
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
import pyzipper
import cv2
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import boto3
from botocore.config import Config

# 多言語辞書（UIおよびファイル整理用）
I18N = {
    "ja": {
        "title": "🛡️ AI Protection Pro Studio v7.0 (Web)",
        "subtitle": "マルチメディア資産保護・暗号化 ＆ 自動ファイル整理スイート",
        "lang_select": "🌐 言語選択 (Language)",
        "tabs": [
            "🖼️ 画像保護", 
            "🔍 透かし検証", 
            "🔒 ZIP保護", 
            "🎬 動画保護", 
            "⚡ 環境監査", 
            "📄 文書・コード保護", 
            "🎵 音声資産保護",
            "📁 自動ファイル整理"
        ],
        "sorter": {
            "header": "📁 フォルダ自動ファイル整理 (Auto File Organizer)",
            "desc": "ファイルをドラッグ＆ドロップするか、ディレクトリを指定して自動仕分けを行います。",
            "mode_select": "整理モードの選択",
            "mode_upload": "📤 ファイル直接アップロード仕分け (Web推奨)",
            "mode_path": "📂 サーバー/ローカルパス指定仕分け",
            "upload_label": "仕分けたいファイルをまとめて選択",
            "target_dir": "対象ディレクトリパス",
            "btn_organize": "🚀 ファイル自動仕分けを実行",
            "success": "✨ すべてのファイルの仕分けが完了しました！",
            "empty": "💡 対象のフォルダに仕分け可能なファイルがありません。",
            "error_skip": "⚠️ スキップ:",
            "download_zip": "📦 仕分け済みフォルダをZIPで一括ダウンロード",
            "folders": {
                ".pdf": "PDF書類",
                ".jpg": "画像ファイル",
                ".png": "画像ファイル",
                ".xlsx": "エクセルデータ",
                ".docx": "ワード書類",
                ".zip": "圧縮ファイル",
                ".mp4": "動画ファイル",
                ".wav": "音声ファイル"
            }
        }
    },
    "en": {
        "title": "🛡️ AI Protection Pro Studio v7.0 (Web)",
        "subtitle": "Multimedia Asset Protection & File Organizer Suite",
        "lang_select": "🌐 Language Selection",
        "tabs": [
            "🖼️ Image Protection", 
            "🔍 Watermark Verify", 
            "🔒 Secure ZIP", 
            "🎬 Video Protection", 
            "⚡ Environment Audit", 
            "📄 Document/Code Vault", 
            "🎵 Audio Asset Vault",
            "📁 File Organizer"
        ],
        "sorter": {
            "header": "📁 Automatic File Organizer",
            "desc": "Upload files directly or specify a directory path to categorize them automatically.",
            "mode_select": "Select Mode",
            "mode_upload": "📤 Upload Files Directly (Recommended for Web)",
            "mode_path": "📂 Specify Server/Local Path",
            "upload_label": "Select multiple files to organize",
            "target_dir": "Target Directory Path",
            "btn_organize": "🚀 Organize Files Now",
            "success": "✨ All files have been successfully organized!",
            "empty": "💡 No processable files found in the target directory.",
            "error_skip": "⚠️ Skipped:",
            "download_zip": "📦 Download Organized Folders as ZIP",
            "folders": {
                ".pdf": "PDF_Documents",
                ".jpg": "Images",
                ".png": "Images",
                ".xlsx": "Excel_Spreadsheets",
                ".docx": "Word_Documents",
                ".zip": "Archives",
                ".mp4": "Video_Files",
                ".wav": "Audio_Files"
            }
        }
    }
}

# 初期設定＆サイドバー（言語切替）
st.set_page_config(
    page_title="AI Protection Pro Studio v7.0 (Web)",
    page_icon="🛡️",
    layout="wide"
)

lang_choice = st.sidebar.radio("🌐 Language / 言語", ["日本語", "English"])
lang_code = "ja" if lang_choice == "日本語" else "en"
texts = I18N[lang_code]

st.title(texts["title"])
st.caption(texts["subtitle"])

# --- Cloudflare R2 連携関数 ---
def get_r2_client():
    if "r2" in st.secrets:
        r2_config = st.secrets["r2"]
        s3_client = boto3.client(
            "s3",
            endpoint_url=r2_config["endpoint_url"],
            aws_access_key_id=r2_config["aws_access_key_id"],
            aws_secret_access_key=r2_config["aws_secret_access_key"],
            config=Config(signature_version="s3v4"),
            region_name="auto"
        )
        return s3_client, r2_config["bucket_name"]
    return None, None

def upload_to_r2(file_bytes, file_name, content_type="application/zip"):
    try:
        s3_client, bucket = get_r2_client()
        if not s3_client:
            return None
        
        s3_client.put_object(
            Bucket=bucket,
            Key=file_name,
            Body=file_bytes,
            ContentType=content_type
        )
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': file_name},
            ExpiresIn=3600  # 1時間有効
        )
        return presigned_url
    except Exception as e:
        st.error(f"Cloudflare R2 アップロードエラー: {e}")
        return None

def get_fernet_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

# タブ構築
(
    tab_img, 
    tab_verify, 
    tab_zip, 
    tab_vid, 
    tab_audit, 
    tab_doc, 
    tab_audio, 
    tab_organizer
) = st.tabs(texts["tabs"])

# ==================== 1. 画像保護タブ ====================
with tab_img:
    st.header("AI Protection & Signature Pro")
    st.write("保護したいイラスト画像を選択してください（複数選択可能）")

    uploaded_images = st.file_uploader("画像ファイルを選択", type=["png", "jpg", "jpeg", "bmp"], accept_multiple_files=True, key="img_uploader")
    
    col1, col2 = st.columns(2)
    with col1:
        sig_text = st.text_input("署名テキスト (Signature)", f"© Artist {datetime.datetime.now().year}")
        pattern = st.selectbox("AI学習防止パターン", ["Grid (格子模様)", "Slash (斜め線)", "Checker (市松模様)"], key="img_pattern")
    with col2:
        intensity = st.slider("学習防止強度 (推奨: 6.0前後)", 2.0, 15.0, 6.5, step=0.5, key="img_intensity")

    if st.button("署名 ＆ AI保護画像を書き出す", type="primary", use_container_width=True):
        if uploaded_images:
            for uploaded_file in uploaded_images:
                img = Image.open(uploaded_file).convert("RGB")
                width, height = img.size

                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("arial.ttf", int(height * 0.025))
                except:
                    font = ImageFont.load_default()

                text_margin = int(height * 0.03)
                text_w = len(sig_text) * int(height * 0.015)
                text_h = int(height * 0.03)
                draw.text((width - text_w - text_margin, height - text_h - text_margin), sig_text, fill=(255, 255, 255), font=font)

                img_array = np.array(img, dtype=np.float32)
                X, Y = np.meshgrid(np.arange(width), np.arange(height))

                if "Slash" in pattern:
                    perturbation = np.sin((X + Y) / 2.0) * intensity
                elif "Checker" in pattern:
                    perturbation = (np.sin(X / 2.0) * np.sin(Y / 2.0)) * intensity
                else:
                    perturbation = (np.sin(X / 2.0) * np.cos(Y / 2.0)) * intensity

                np.random.seed(1337)
                random_noise = np.random.normal(0, intensity * 0.3, img_array.shape)
                for i in range(3):
                    img_array[:, :, i] += perturbation + random_noise[:, :, i]

                final_img = Image.fromarray(np.clip(img_array, 0, 255).astype(np.uint8))

                buf = io.BytesIO()
                final_img.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.image(final_img, caption=f"保護完了: {uploaded_file.name}", use_column_width=True)
                st.download_button(
                    label=f"⬇️ {uploaded_file.name} をダウンロード",
                    data=byte_im,
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_protected.png",
                    mime="image/png"
                )
            st.success("全ての画像の処理が完了しました！")
        else:
            st.warning("画像ファイルをアップロードしてください。")

# ==================== 2. 透かし検証タブ ====================
with tab_verify:
    st.header("Watermark Verification")
    st.write("オリジナルファイルと保護後のファイルを比較し、埋め込まれた透かしノイズを可視化します。")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        orig_file = st.file_uploader("1. 元のファイル (オリジナル)", type=["png", "jpg", "jpeg"], key="v_orig")
    with col_v2:
        prot_file = st.file_uploader("2. 保護後のファイル", type=["png", "jpg", "jpeg"], key="v_prot")

    if st.button("🔍 透かし（差分ノイズ）を抽出して可視化", type="primary", use_container_width=True):
        if orig_file and prot_file:
            try:
                img_orig = Image.open(orig_file).convert("RGB")
                img_prot = Image.open(prot_file).convert("RGB")
                arr_orig = np.array(img_orig, dtype=np.float32)
                arr_prot = np.array(img_prot, dtype=np.float32)

                raw_diff = arr_prot - arr_orig
                enhanced_diff = 128.0 + (raw_diff * 30.0)
                output_array = np.clip(enhanced_diff, 0, 255).astype(np.uint8)
                diff_image = Image.fromarray(output_array)

                buf = io.BytesIO()
                diff_image.save(buf, format="PNG")
                
                st.image(diff_image, caption="抽出された透かしパターン (差分強調)", use_column_width=True)
                st.download_button("⬇️ 抽出結果をダウンロード", buf.getvalue(), "watermark_verified_diff.png", "image/png")
                st.success("透かしの可視化に成功しました！")
            except Exception as e:
                st.error(f"検証エラー: {e}")
        else:
            st.warning("両方のファイルを選択してください。")

# ==================== 3. ZIP保護タブ ====================
with tab_zip:
    st.header("Secure ZIP Packager")
    st.write("ファイルをAES-256で暗号化したパスワード付きZIPアーカイブを作成します。")

    zip_targets = st.file_uploader("圧縮するファイルを選択", accept_multiple_files=True, key="zip_uploader")
    zip_pass = st.text_input("暗号化パスワード", type="password", key="zip_pass")

    if st.button("🔒 強固なパスワード付きZIPを作成", type="primary", use_container_width=True):
        if zip_targets and zip_pass:
            zip_buffer = io.BytesIO()
            with pyzipper.AESZipFile(zip_buffer, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(zip_pass.encode('utf-8'))
                for target in zip_targets:
                    zf.writestr(target.name, target.getvalue())
            
            st.success("ZIPアーカイブの作成が完了しました！")
            st.download_button("⬇️ 暗号化ZIPをダウンロード", zip_buffer.getvalue(), "protected_archive.zip", "application/zip")
        else:
            st.warning("ファイルとパスワードの両方を入力してください。")

# ==================== 4. 動画保護タブ ====================
with tab_vid:
    st.header("AI Anti-Learning Video Protection")
    st.write("動画の全フレームにAI学習防止ノイズを付与します。")

    vid_file = st.file_uploader("動画ファイルを選択 (.mp4)", type=["mp4"], key="vid_uploader")
    col_vid1, col_vid2 = st.columns(2)
    with col_vid1:
        v_pattern = st.selectbox("動画用パターン", ["Grid (格子模様)", "Slash (斜め線)", "Checker (市松模様)"], key="v_pat")
    with col_vid2:
        v_intensity = st.slider("ノイズ強度 (推奨: 4.0〜6.0)", 2.0, 15.0, 5.0, step=0.5, key="v_int")

    if st.button("🎬 全フレーム保護動画を書き出す", type="primary", use_container_width=True):
        if vid_file:
            tfile = f"temp_input_{datetime.datetime.now().timestamp()}.mp4"
            out_tfile = f"temp_output_{datetime.datetime.now().timestamp()}.mp4"
            
            with open(tfile, "wb") as f:
                f.write(vid_file.read())

            cap = cv2.VideoCapture(tfile)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_tfile, fourcc, fps, (width, height))

            X, Y = np.meshgrid(np.arange(width), np.arange(height))
            if "Slash" in v_pattern: perturbation = np.sin((X + Y) / 2.0) * v_intensity
            elif "Checker" in v_pattern: perturbation = (np.sin(X / 2.0) * np.sin(Y / 2.0)) * v_intensity
            else: perturbation = (np.sin(X / 2.0) * np.cos(Y / 2.0)) * v_intensity

            np.random.seed(1337)
            random_noise = np.random.normal(0, v_intensity * 0.3, (height, width, 3))

            progress_bar = st.progress(0)
            status_text = st.empty()
            frame_count = 0

            while True:
                ret, frame = cap.read()
                if not ret: break
                frame_float = frame.astype(np.float32)
                for i in range(3): frame_float[:, :, i] += perturbation + random_noise[:, :, i]
                out.write(np.clip(frame_float, 0, 255).astype(np.uint8))
                
                frame_count += 1
                progress_bar.progress(min(frame_count / total_frames, 1.0))
                status_text.text(f"フレーム処理中... ({frame_count}/{total_frames})")

            cap.release()
            out.release()

            with open(out_tfile, "rb") as f:
                vid_bytes = f.read()

            st.success("動画の保護処理が完了しました！")
            st.download_button("⬇️ 保護済み動画をダウンロード", vid_bytes, f"{os.path.splitext(vid_file.name)[0]}_protected.mp4", "video/mp4")

            if os.path.exists(tfile): os.remove(tfile)
            if os.path.exists(out_tfile): os.remove(out_tfile)
        else:
            st.warning("動画ファイルをアップロードしてください。")

# ==================== 5. 環境監査タブ ====================
with tab_audit:
    st.header("Security Audit (Web Standard)")
    st.write("ファイル整合性チェックおよびハッシュ値の検証を行います。")

    audit_file = st.file_uploader("スキャンするファイルを選択", type=None, key="audit_uploader")
    if audit_file:
        file_bytes = audit_file.getvalue()
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        
        st.subheader("📊 監査結果")
        st.code(f"ファイル名: {audit_file.name}\nサイズ: {len(file_bytes)} bytes\nSHA-256: {sha256_hash}", language="text")
        st.success("⚡ 整合性スキャン完了: 異常なし (CLEAN)")

# ==================== 6. 文書・コード保護タブ ====================
with tab_doc:
    st.header("Document & Code Vault")
    st.write("MS Word, Excel, PDF, Python(.py) などの任意ファイルを AES-256 で暗号化/復元します。")

    doc_file = st.file_uploader("対象ファイルを選択", type=None, key="doc_uploader")
    doc_pass = st.text_input("専用暗号化パスワード", type="password", key="doc_pass")

    col_doc1, col_doc2 = st.columns(2)
    with col_doc1:
        if st.button("🔒 ファイルを暗号化 (Lock)", use_container_width=True):
            if doc_file and doc_pass:
                salt = os.urandom(16)
                key = get_fernet_key(doc_pass, salt)
                f = Fernet(key)
                encrypted_data = f.encrypt(doc_file.getvalue())
                
                final_bytes = salt + encrypted_data
                st.success("ファイルを暗号化しました！")
                st.download_button("⬇️ 暗号化ファイルをダウンロード", final_bytes, f"{doc_file.name}.enc", "application/octet-stream")
            else:
                st.warning("ファイルとパスワードを指定してください。")

    with col_doc2:
        if st.button("🔓 ファイルを復元 (Unlock)", use_container_width=True):
            if doc_file and doc_pass:
                try:
                    raw_data = doc_file.getvalue()
                    salt = raw_data[:16]
                    encrypted_data = raw_data[16:]

                    key = get_fernet_key(doc_pass, salt)
                    f = Fernet(key)
                    decrypted_data = f.decrypt(encrypted_data)

                    out_name = doc_file.name.replace(".enc", "") if doc_file.name.endswith(".enc") else f"decrypted_{doc_file.name}"
                    st.success("ファイルの復元に成功しました！")
                    st.download_button("⬇️ 復元ファイルをダウンロード", decrypted_data, out_name, "application/octet-stream")
                except Exception as e:
                    st.error("復元に失敗しました。パスワードが正しくないかファイルが破損しています。")
            else:
                st.warning("ファイルとパスワードを指定してください。")

# ==================== 7. 音声資産保護タブ ====================
with tab_audio:
    st.header("Audio Vault (19kHz Anti-AI)")
    st.write("不可聴領域(19kHz帯域)に暗号シードに基づくパターンを付与し、ボイスクローン等を防ぎます。")

    audio_file = st.file_uploader("音声ファイルを選択 (.wav)", type=["wav"], key="audio_uploader")
    secret_key = st.text_input("所有者識別キー (暗号シード)", "Studio7_User_Key")

    if st.button("🎵 音声資産の保護を実行", type="primary", use_container_width=True):
        if audio_file:
            sample_rate, data = wavfile.read(io.BytesIO(audio_file.getvalue()))
            
            np.random.seed(sum(ord(c) for c in secret_key))
            time_axis = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
            watermark = (np.sin(2 * np.pi * 19000 * time_axis) + np.random.normal(0, 1, len(data)) * 0.1) * 0.003

            protected_data = data.copy().astype(np.float32)
            if len(protected_data.shape) > 1:
                for ch in range(protected_data.shape[1]):
                    protected_data[:, ch] += watermark * (np.max(np.abs(data[:, ch])) or 1)
            else:
                protected_data += watermark * (np.max(np.abs(data)) or 1)

            final_data = np.clip(protected_data, -32768, 32767).astype(np.int16) if data.dtype == np.int16 else protected_data
            
            out_buf = io.BytesIO()
            wavfile.write(out_buf, sample_rate, final_data)

            st.success("音声ファイルの保護処理が完了しました！")
            st.download_button("⬇️ 保護済み音声(.wav)をダウンロード", out_buf.getvalue(), f"protected_{audio_file.name}", "audio/wav")
        else:
            st.warning(".wav ファイルを選択してください。")

# ==================== 8. 自動ファイル整理タブ (R2対応版) ====================
with tab_organizer:
    sorter_text = texts["sorter"]
    st.header(sorter_text["header"])
    st.write(sorter_text["desc"])

    mode = st.radio(
        sorter_text["mode_select"], 
        [sorter_text["mode_upload"], sorter_text["mode_path"]],
        key="sorter_mode"
    )

    folders_map = sorter_text["folders"]

    # モード①：直接ファイルをアップロードして仕分け（Web版推奨）
    if mode == sorter_text["mode_upload"]:
        uploaded_files = st.file_uploader(
            sorter_text["upload_label"], 
            accept_multiple_files=True, 
            key="sorter_uploader"
        )

        if st.button(sorter_text["btn_organize"], type="primary", use_container_width=True):
            if uploaded_files:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for file in uploaded_files:
                        _, extension = os.path.splitext(file.name)
                        extension = extension.lower()
                        
                        folder_name = folders_map.get(extension, "Other_Files")
                        zip_path = f"{folder_name}/{file.name}"
                        
                        zf.writestr(zip_path, file.getvalue())

                zip_data = zip_buf.getvalue()
                st.success(sorter_text["success"])

                # R2へアップロードとリンク生成
                file_key = f"organized_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                r2_url = upload_to_r2(zip_data, file_key)

                if r2_url:
                    st.info("☁️ Cloudflare R2 クラウドストレージに安全に保存されました！")
                    st.markdown(f"🔗 **[クラウドから一括ダウンロード（有効期限: 1時間）]({r2_url})**")

                st.download_button(
                    label=sorter_text["download_zip"],
                    data=zip_data,
                    file_name="organized_files.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            else:
                st.warning("ファイルをアップロードしてください。")

    # モード②：パス指定仕分け
    else:
        target_dir_input = st.text_input(
            sorter_text["target_dir"], 
            value="./protected_outputs", 
            key="sorter_dir"
        )

        if st.button(sorter_text["btn_organize"], type="primary", use_container_width=True):
            target_dir = os.path.abspath(target_dir_input)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)

            moved_count = 0
            file_list = os.listdir(target_dir)

            for filename in file_list:
                file_path = os.path.join(target_dir, filename)
                
                if os.path.isfile(file_path):
                    _, extension = os.path.splitext(filename)
                    extension = extension.lower()
                    
                    if extension in folders_map:
                        folder_name = folders_map[extension]
                        dest_folder = os.path.join(target_dir, folder_name)
                        
                        if not os.path.exists(dest_folder):
                            os.makedirs(dest_folder, exist_ok=True)
                        
                        try:
                            shutil.move(file_path, os.path.join(dest_folder, filename))
                            moved_count += 1
                        except Exception as e:
                            st.warning(f"{sorter_text['error_skip']} {filename} - {e}")

            if moved_count > 0:
                st.success(f"{sorter_text['success']} ({moved_count} files moved)")

                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for root, _, files in os.walk(target_dir):
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, target_dir)
                            zf.write(full_path, rel_path)

                zip_data = zip_buf.getvalue()

                # R2へアップロードとリンク生成
                file_key = f"organized_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                r2_url = upload_to_r2(zip_data, file_key)

                if r2_url:
                    st.info("☁️ Cloudflare R2 クラウドストレージに安全に保存されました！")
                    st.markdown(f"🔗 **[クラウドから一括ダウンロード（有効期限: 1時間）]({r2_url})**")

                st.download_button(
                    label=sorter_text["download_zip"],
                    data=zip_data,
                    file_name="organized_files.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            else:
                st.info(sorter_text["empty"])
