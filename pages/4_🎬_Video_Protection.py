import streamlit as st
import cv2
import numpy as np
import tempfile
import os

st.header("AI Anti-Learning Video Protection")

# Pro判定
is_pro = st.session_state.get("is_pro", False)

if not is_pro:
    st.error("🔒 この機能は Pro プラン限定です。")
    st.info("サイドバーからキーを入力するとロックが解除されます。")
else:
    st.write("動画の全フレームにAI学習防止ノイズを付与します。")
    video_file = st.file_uploader("動画ファイルを選択 (.mp4)", type=["mp4"], key="vid_file")
    
    col1, col2 = st.columns(2)
    with col1:
        pattern = st.selectbox("動画用パターン", ["Grid (格子模様)", "Slash (斜め線)", "Checker (市松模様)"], key="vid_pattern")
    with col2:
        intensity = st.slider("ノイズ強度 (推奨: 4.0〜6.0)", 1.0, 10.0, 4.0, key="vid_intensity")

    if st.button("🎬 全フレーム保護動画を書き出す", type="primary", use_container_width=True):
        if video_file:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(video_file.read())
            tfile.close()

            cap = cv2.VideoCapture(tfile.name)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            out_tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            out_path = out_tfile.name
            out_tfile.close()

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

            X, Y = np.meshgrid(np.arange(width), np.arange(height))
            if pattern == "Slash (斜め線)":
                perturbation = np.sin((X + Y) / 2.0) * intensity
            elif pattern == "Checker (市松模様)":
                perturbation = (np.sin(X / 2.0) * np.sin(Y / 2.0)) * intensity
            else:
                perturbation = (np.sin(X / 2.0) * np.cos(Y / 2.0)) * intensity

            progress_bar = st.progress(0)
            frame_idx = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_f = frame.astype(np.float32)
                for i in range(3):
                    frame_f[:, :, i] += perturbation
                
                protected_frame = np.clip(frame_f, 0, 255).astype(np.uint8)
                out.write(protected_frame)

                frame_idx += 1
                if total_frames > 0:
                    progress_bar.progress(min(frame_idx / total_frames, 1.0))

            cap.release()
            out.release()
            os.unlink(tfile.name)

            st.success("動画の保護処理が完了しました！")
            with open(out_path, "rb") as f:
                st.download_button(
                    label="⬇️ 保護済み動画をダウンロード",
                    data=f.read(),
                    file_name="protected_video.mp4",
                    mime="video/mp4"
                )
        else:
            st.warning("動画ファイルをアップロードしてください。")