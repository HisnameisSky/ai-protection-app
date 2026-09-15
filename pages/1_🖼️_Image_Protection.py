# pages/1_🖼️_Image_Protection.py
import streamlit as st
import io
import os
import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

st.header("AI Protection & Signature Pro")
st.write("保護したいイラスト画像を選択してください（複数選択可能）")

uploaded_images = st.file_uploader("画像ファイルを選択", type=["png", "jpg", "jpeg", "bmp"], accept_multiple_files=True)

col1, col2 = st.columns(2)
with col1:
    sig_text = st.text_input("署名テキスト (Signature)", f"© Artist {datetime.datetime.now().year}")
    pattern = st.selectbox("AI学習防止パターン", ["Grid (格子模様)", "Slash (斜め線)", "Checker (市松模様)"])
with col2:
    intensity = st.slider("学習防止強度 (推奨: 6.0前後)", 2.0, 15.0, 6.5, step=0.5)

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

            if pattern == "Slash (斜め線)":
                perturbation = np.sin((X + Y) / 2.0) * intensity
            elif pattern == "Checker (市松模様)":
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
            
            st.image(final_img, caption=f"Protected: {uploaded_file.name}", use_container_width=True)                
            st.download_button(
                label=f"⬇️ {uploaded_file.name} をダウンロード",
                data=buf.getvalue(),
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_protected.png",
                mime="image/png"
            )
        st.success("全ての画像の処理が完了しました！")
    else:
        st.warning("画像ファイルをアップロードしてください。")