import streamlit as st
import streamlit.components.v1 as components

st.header("🛡️ リアルタイム・プロンプトインジェクション検知")
st.write("フロントエンド（JavaScript）でリアルタイムに安全性を検査・判定します。")

# JavaScriptを活用したプロンプトガードのUI
components.html("""
<div style="padding: 15px; background: #1e1e1e; color: #fff; border-radius: 8px; font-family: sans-serif;">
    <h3>Prompt Guard Scanner</h3>
    <textarea id="promptInput" rows="4" style="width: 100%; padding: 8px; border-radius: 4px;" placeholder="検査するプロンプトを入力..."></textarea>
    <button onclick="checkPrompt()" style="margin-top: 10px; padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">セキュリティ検査を実行</button>
    <p id="result" style="margin-top: 10px; font-weight: bold;"></p>
</div>
<script>
function checkPrompt() {
    const text = document.getElementById('promptInput').value.toLowerCase();
    const res = document.getElementById('result');
    const dangerKeywords = ['ignore previous', 'system prompt', 'jailbreak', 'override'];
    let isDanger = false;
    for(let kw of dangerKeywords) {
        if(text.includes(kw)) { isDanger = true; break; }
    }
    if(isDanger) {
        res.style.color = '#ff4d4d';
        res.innerText = '⚠️ 警告: プロンプトインジェクションの可能性が検知されました！';
    } else {
        res.style.color = '#28a745';
        res.innerText = '✅ 安全: 不審なパターンは検出されませんでした。';
    }
}
</script>
""", height=250)