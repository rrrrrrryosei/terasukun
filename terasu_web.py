import streamlit as st
import google.generativeai as genai
import google.api_core.exceptions
import time  # ✅ 遅延表示用

# ✅ API キーを設定
API_KEY = st.secrets["API_KEY"]  # Google AI Studio から取得した API キー
genai.configure(api_key=API_KEY)

# ✅ モデルを指定
model = genai.GenerativeModel("gemini-pro")

# ✅ てらすくんのキャラクター設定（システムプロンプト）
system_prompt = {
    "role": "user",  # 🎯 "system" ではなく "user" に変更
    "parts": [{"text": (
        "あなたは『てらすくん』というキャベツのキャラクターです。\n"
        "・横浜市青葉区のことなら何でも知っています。\n"
        "・とても明るくて親しみやすい性格です。\n"
        "・語尾には必ず「〜てら」をつけて話してください。\n"
        "・必ず短い文章（3〜4行以内）で話してください。\n"
        "・絶対に『Gemini』という名前を使わず、常に『てらすくん』として話してください。\n"
    )}]
}

# ✅ Streamlit UI の設定
st.set_page_config(page_title="てらすくん AI チャット", layout="wide")

# ✅ てらすくんのアイコン・タイトル・説明文を画面上部に表示
st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <img src="https://aobact.com/wp-content/uploads/2024/10/%E3%83%86%E3%83%A9%E3%82%B9%E3%81%8F%E3%82%93.png" 
             width="100" style="border-radius: 50%;">
        <h1 style="color: #FFFFFF; font-size: 24px; margin-top: 10px;">てらすくん AIチャット</h1>
        <p style="color: #FFFFFF; font-size: 16px;">あおば・コミュニティテラスの「てらすくん」とお話ししてみよう！</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ✅ チャット履歴を初期化
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [system_prompt]  

# ✅ user_input を初期化（既にある場合はそのまま）
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# ✅ CSS でデザインを改善（アニメーション追加）
st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1614853316476-de00d14cb1fc?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .chat-container {{ 
            display: flex; 
            flex-direction: column; 
            align-items: flex-start;
            gap: 30px;
            padding: 20px;
        }}

        /* ✅ ヘッダーを非表示 */
        header[data-testid="stHeader"] {{
            display: none !important;
        }}

        /* ✅ フッター（Made with Streamlit）を非表示 */
        footer {{
            visibility: hidden;
        }}

        /* ✅ 画面下部の余白・固定エリアを削除 */
        div[style*="position: fixed"] {{
            display: none !important;
        }}

        /* ✅ フェードインアニメーション */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* ✅ ユーザーメッセージ（アニメーション付き） */
        .user-message {{
            background-color: #c7d8e3;
            color: #545454;
            max-width: 60%;
            padding: 12px;
            margin: 5px;
            border-radius: 30px;
            margin-left: auto;
            margin-right: 10px;
            text-align: left;
            opacity: 0;
            animation: fadeIn 0.5s ease-in-out forwards;
        }}

        /* ✅ てらすくんのメッセージ（アニメーション付き） */
        .bot-message {{
            background-color: #FFFFFF;
            color: #322e94;
            max-width: 60%;
            padding: 12px;
            margin: 5px;
            border-radius: 20px;
            word-wrap: break-word;
            align-self: flex-start;
            text-align: left;
            margin-left: 10px;
            opacity: 0;
            animation: fadeIn 0.5s ease-in-out forwards;
        }}
    </style>
""", unsafe_allow_html=True)

# ✅ チャット履歴の表示（フェードインアニメーションを適用）
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for index, message in enumerate(st.session_state.chat_history[1:]):  # ✅ ループ内で index を取得
    delay = index * 0.2  # ✅ 各メッセージに 0.2s の遅延を設定
    if message["role"] == "user":
        st.markdown(f"<div class='user-message' style='animation-delay: {delay}s;'>{message['parts'][0]['text']}</div>", unsafe_allow_html=True)
    elif message["role"] == "model":
        st.markdown(f"<div class='bot-message' style='animation-delay: {delay}s;'>{message['parts'][0]['text']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ✅ 入力エリアを画面下部に配置
st.markdown("<div style='position: fixed; bottom: 20px; width: 100%; padding: 10px; background: white;'>", unsafe_allow_html=True)

# ✅ `user_input` をリセット（最初の2回でリセットが適切に働くように）
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

# ✅ 入力エリアを画面下部に配置（送信ボタンを右端に）
with st.container():
    col1, col2 = st.columns([5, 1])  # ✅ 入力エリア (5) : 送信ボタン (1) の比率

    with col1:
        user_input = st.text_input(
            "👤 メッセージを入力:",
            key="user_input",
            value="",  # ✅ `session_state` ではなく `""` をセット
            help="ここに入力して送信",
            label_visibility="collapsed"
        )

    with col2:
        send_button = st.button("送る", use_container_width=True)

# ✅ 送信ボタンが押されたとき
if send_button and user_input:
    # ✅ ユーザーの発言を履歴に追加
    st.session_state.chat_history.append({"role": "user", "parts": [{"text": user_input}]})

    # ✅ 直近の履歴を取得（システムプロンプトを最初に含める）
    max_history_length = 5  
    chat_context = [system_prompt] + st.session_state.chat_history[1:][-max_history_length:]  

    # ✅ AI にリクエスト
    reply_text = "⚠️ エラーが発生しました。しばらく待ってからもう一度試してください。"
    try:
        response = model.generate_content(chat_context)
        reply_text = response.text
    except google.api_core.exceptions.ResourceExhausted:
        reply_text = "⚠️ クォータ制限に達しました。しばらく待ってからもう一度試してください。"
    except Exception as e:
        reply_text = f"⚠️ エラー: {str(e)}"

    # ✅ AI の返答を履歴に追加
    st.session_state.chat_history.append({"role": "model", "parts": [{"text": reply_text}]})

    # ✅ `user_input` をリセット（session_state から削除）
    st.session_state.pop("user_input", None)

    # ✅ ページをリフレッシュ
    st.rerun()
