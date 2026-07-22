import streamlit as st

st.title("AI Protection Pro")

user_input = st.text_input("チェックしたいデータを入力")


if st.button("実行"):
    
    result = f"処理完了: {user_input}"
    st.success(f"結果: {result}")