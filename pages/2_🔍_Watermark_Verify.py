import streamlit as st
import numpy as np
from PIL import Image
import io

st.header("Watermark Verification")
st.desc = "オリジナルファイルと保護後のファイルを比較し、埋め込まれた透かしノイズを可視化します。"
st.write(st.desc)

col1, col2 = st.columns(2)
with col1:
    orig_file = st.file_uploader("1. 元のファイル (オリジナル)", type=["png", "jpg", "jpeg"], key="verify_orig")
with col2:
    prot_file = st.file_uploader("2. 保護後のファイル", type=["png", "jpg", "jpeg"], key="verify_prot")

if st.button("🔍 透かし（差分ノイズ）を抽出して可視化", type="primary", use_container_width=True):
    if orig_file and prot_file:
        img_orig = Image.open(orig_file).convert("RGB")
        img_prot = Image.open(prot_file).convert("RGB")
        
        if img_orig.size != img_prot.size:
            img_prot = img_prot.resize(img_orig.size)

        arr_orig = np.array(img_orig, dtype=np.float32)
        arr_prot = np.array(img_prot, dtype=np.float32)

        # 差分を抽出して強調
        diff = np.abs(arr_prot - arr_orig) * 10.0
        diff_img = Image.fromarray(np.clip(diff, 0, 255).astype(np.uint8))

        st.image(diff_img, caption="抽出された透かしパターン (差分強調)", use_container_width=True)
        
        buf = io.BytesIO()
        diff_img.save(buf, format="PNG")
        st.download_button(
            label="⬇️ 抽出結果をダウンロード",
            data=buf.getvalue(),
            file_name="watermark_diff.png",
            mime="image/png"
        )
        st.success("透かしの可視化に成功しました！")
    else:
        st.warning("両方のファイルを選択してください。")