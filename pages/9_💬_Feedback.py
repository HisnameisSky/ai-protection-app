import streamlit as st
from utils.auth import send_feedback

st.header("💬 ご意見・改善提案 (Feedback & Requests)")
st.write("サービスの改善や新機能の要望、バグ報告などをぜひお寄せください。")

category = st.selectbox("お問い合わせ種別", ["💡 機能の改善提案", "🐛 バグ・不具合報告", "✨ 新機能のリクエスト", "💬 その他"])
content = st.text_area("メッセージ内容", placeholder="例: 〇〇の処理速度を上げてほしい、など")
email = st.text_input("返信先メールアドレス (任意)", placeholder="name@example.com")

if st.button("✉️ フィードバックを送信", type="primary", use_container_width=True):
    if content.strip():
        success = send_feedback(category, content, email)
        if success:
            st.success("🎉 フィードバックをお送りいただきありがとうございます！今後の開発の参考にさせていただきます。")
    else:
        st.warning("⚠️ メッセージ内容を入力してください。")