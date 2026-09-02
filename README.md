<img width="1477" height="759" alt="スクリーンショット 2026-07-28 16 54 56" src="https://github.com/user-attachments/assets/7f2d9aa7-b7da-4886-8cff-86656649deb5" />

# 🛜アクセスリンク先（Access Link below）：
[https://ai-protection-studio.streamlit.app/
](https://ai-protection-studio.streamlit.app/)
# 🛡️ AI Protection Pro Studio v7.0 (Web Edition)

An all-in-one web application designed to protect digital assets—images, videos, audio, and documents—from unauthorized AI training, voice cloning, and data leakage.

AIによる無断学習、ボイスクローン、情報漏洩からクリエイターのデジタル資産（画像・動画・音声・文書）を守るオールインワンWebアプリケーションです。

---

## ✨ Features / 主な機能

**🛡️ Prompt Guard (プロンプトインジェクション検知) *NEW!***
  - Detects and blocks prompt injection and system prompt extraction attacks in real-time using pattern matching.
  - パターンマッチングにより、指示無視やシステムプロンプト抽出などの不正な入力（プロンプトインジェクション）をリアルタイムに検知・ブロック。

**🖼️ Image Protection & Signature (画像保護 & 署名)**
  - Protects illustrations from AI scraping with multi-pattern noise (`Grid`, `Slash`, `Checker`).
  - Inserts customizable signatures with automated font scaling.

**🔍 Watermark Verification (透かし検証)**
  - Extracts and visualizes difference noise to verify invisible watermarks.

**🔒 Secure ZIP Packager (暗号化ZIP作成)**
  - Packages files into encrypted ZIP archives using AES-256.

**🎬 Anti-AI Video Protection (動画保護)**
  - Applies frame-by-frame anti-learning noise to .mp4 videos.

**⚡ Security Audit (環境監査)**
  - Scans and verifies file integrity using SHA-256 cryptographic hashes.

**📄 Document & Code Vault (文書・コード暗号化)**
  - Encrypts and decrypts sensitive documents (Word, PDF, .py) using Fernet (AES-256).

**🎵 Audio Vault (19kHz Anti-AI 音声保護)**
  - Embeds non-audible 19kHz signature noise to neutralize AI voice cloning tools.

**📁 Automatic File Organizer (自動ファイル整理)**
  - Automatically categorizes and organizes uploaded files by file extension.

---

## 🛠️ Tech Stack / 使用技術

- UI Framework: Streamlit
- Security & Guard: Regex Pattern Matching (Prompt Injection Defense), Cryptography (Fernet / PBKDF2HMAC), PyZipper
- Image / Video Processing: Pillow, OpenCV (opencv-python-headless), NumPy
- Audio Processing: SciPy
- Backend & Cloud: Supabase (Authentication/Database), Cloudflare R2 (Storage), Resend (Email API)

---

## 📜 License
Distributed under the MIT License. See LICENSE for more information.

---

## 🚀 Quick Start / 使い方

### Local Run (ローカル実行)

```bash
# 1. Clone this repository
git clone https://github.com/HisnameisSky/ai-protection-app.name.git)
cd ai-protection-app.name

# 2. Install required packages
pip install -r requirements.txt

# 3. Run Streamlit App
streamlit run app.py
```
---

### デスクトップ版アプリなら：
### For desktop-app version:
https://github.com/HisnameisSky/ai-protection-pro-v7

