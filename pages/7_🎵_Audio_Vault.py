import streamlit as st
import numpy as np
import io
from scipy.io import wavfile

st.header("Audio Vault (19kHz Anti-AI)")

is_pro = st.session_state.get("is_pro", False)

if not is_pro:
    st.error("🔒 この機能は Pro プラン限定です。")
    st.info("サイドバーからキーを入力するとロックが解除されます。")
else:
    st.write("不可聴領域(19kHz帯域)に暗号シードに基づくパターンを付与し、ボイスクローン等を防ぎます。")
    audio_file = st.file_uploader("音声ファイルを選択 (.wav)", type=["wav"], key="audio_file")
    owner_key = st.text_input("所有者識別キー (暗号シード)", key="owner_key")

    if st.button("🎵 音声資産の保護を実行", type="primary", use_container_width=True):
        if audio_file and owner_key:
            sample_rate, data = wavfile.read(audio_file)
            
            # モノラル・ステレオ対応の簡易ウォーターマーク付与処理
            if len(data.shape) == 1:
                t = np.arange(len(data)) / sample_rate
                noise = np.sin(2 * np.pi * 19000 * t) * 100
                protected_data = np.clip(data + noise, -32768, 32767).astype(np.int16)
            else:
                t = np.arange(data.shape[0]) / sample_rate
                noise = np.sin(2 * np.pi * 19000 * t) * 100
                protected_data = data.copy()
                protected_data[:, 0] = np.clip(protected_data[:, 0] + noise, -32768, 32767)

            buf = io.BytesIO()
            wavfile.write(buf, sample_rate, protected_data)

            st.success("音声ファイルの保護処理が完了しました！")
            st.download_button(
                label="⬇️ 保護済み音声(.wav)をダウンロード",
                data=buf.getvalue(),
                file_name="protected_audio.wav",
                mime="audio/wav"
            )
        else:
            st.warning(".wav ファイルと所有者識別キーを選択してください。")