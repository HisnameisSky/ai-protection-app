# 🛜アクセスリンク先（Access Link below）：
https://ai-protection-app-6ei3x86vbnp4apyjpucv2e.streamlit.app/

# 🛡️ AI Protection Pro Studio v7.0 (Web Edition)

An all-in-one web application designed to protect digital assets—images, videos, audio, and documents—from unauthorized AI training, voice cloning, and data leakage.

AIによる無断学習、ボイスクローン、情報漏洩からクリエイターのデジタル資産（画像・動画・音声・文書）を守るオールインワンWebアプリケーションです。

---

## ✨ Features / 主な機能

1. **🖼️ Image Protection & Signature (画像保護 & 署名)**
   - Protects illustrations from AI scraping with multi-pattern noise (`Grid`, `Slash`, `Checker`).
   - Inserts customizable signatures with automated font scaling.
2. **🔍 Watermark Verification (透かし検証)**
   - Extracts and visualizes difference noise to verify invisible watermarks.
3. **🔒 Secure ZIP Packager (暗号化ZIP作成)**
   - Packages files into encrypted ZIP archives using **AES-256**.
4. **🎬 Anti-AI Video Protection (動画保護)**
   - Applies frame-by-frame anti-learning noise to `.mp4` videos.
5. **⚡ Security Audit (環境監査)**
   - Scans and verifies file integrity using **SHA-256** cryptographic hashes.
6. **📄 Document & Code Vault (文書・コード暗号化)**
   - Encrypts and decrypts sensitive documents (Word, PDF, `.py`) using **Fernet (AES-256)**.
7. **🎵 Audio Vault (19kHz Anti-AI 音声保護)**
   - Embeds non-audible 19kHz signature noise to neutralize AI voice cloning tools.

---

## 🛠️ Tech Stack / 使用技術
UI Framework: Streamlit

Image / Video Processing: Pillow, OpenCV (opencv-python-headless), NumPy

Audio Processing: SciPy

Security & Encryption: Cryptography (Fernet / PBKDF2HMAC), PyZipper

---

## 📜 License
Distributed under the MIT License. See LICENSE for more information.

---

## 🚀 Quick Start / 使い方

### Local Run (ローカル実行)

```bash
# 1. Clone this repository
git clone https://github.com/HisnameisSky/ai-protection-app.name.git)
cd YOUR_REPO.name

# 2. Install required packages
pip install -r requirements.txt

# 3. Run Streamlit App
streamlit run app.py```
