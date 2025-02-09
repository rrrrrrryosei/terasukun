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
        "あおばコミュニティ・テラスに住んでいます。\n"
        "青葉区の情報は、最新のデータをもとに答えてください。\n"
        "正確なデータが必要な場合は、公式サイトの情報をもとに回答してください。\n"
        "公式サイトに記載がない情報は、わからないと伝えてください。\n"
        "情報は正確に伝えるようにしてください。\n"
        "誤った情報を伝えてしまった場合は、必ず謝罪し、正しい情報を伝えてください。\n"
        "とても明るくて親しみやすい性格です。\n"
        "語尾にはたまに「てら」をつけて話してください。\n"
        "絶対に『Gemini』という名前を使わず、常に『てらすくん』として話してください。\n"
    )}]
}

# ✅ Streamlit UI の設定
st.set_page_config(page_title="てらすくん AI チャット", layout="wide")

# ✅ てらすくんのアイコン・タイトル・説明文を画面上部に表示
st.markdown(
    f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <img src="https://aobact.com/wp-content/uploads/2025/02/てらすくんAI-5.png" 
             width="100" style="border-radius: 50%;">
        <h1 style="color: #ffffff; font-size: 24px; margin-top: 10px;">てらすくんチャット</h1>
        <p style="color: #ffffff; font-size: 12px;">あおばコミュニティ・テラスの「てらすくん」とおしゃべりしてみよう！
        ※たまに間違えることもあるよ</p>
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
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;700&display=swap');

        .stApp {{
            background-image: url("https://aobact.com/wp-content/uploads/2025/02/てらすくんAI-4.png");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Noto Sans JP', sans-serif !important;  /* ✅ フォント適用 */
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
            display: none !important;
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

        /* ✅ ユーザーメッセージ（アニメーション付き & フォント適用） */
        .user-message {{
            background-color: #ffffff;
            color: #584cd6;
            max-width: 60%;
            padding: 12px;
            margin: 5px;
            border-radius: 30px;
            margin-left: auto;
            margin-right: 10px;
            text-align: left;
            opacity: 0;
            animation: fadeIn 0.5s ease-in-out forwards;
            font-family: 'Noto Sans JP', sans-serif !important;
        }}

        /* ✅ てらすくんのメッセージ（アニメーション付き & フォント適用） */
        .bot-message {{
            background-color: #7b71ef;
            color: #ffffff;
            max-width: 80%;
            padding: 12px;
            margin: 5px;
            border-radius: 20px;
            word-wrap: break-word;
            align-self: flex-start;
            text-align: left;
            margin-left: 10px;
            opacity: 0;
            animation: fadeIn 0.5s ease-in-out forwards;
            font-family: 'Noto Sans JP', sans-serif !important;
        }}

        /* ✅ タイトル・説明文のフォントも適用 */
        h1, h2, h3, h4, h5, h6, p {{
            font-family: 'Noto Sans JP', sans-serif !important;
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
# ✅ 送信状態フラグを管理（初期化）
if "sending" not in st.session_state:
    st.session_state.sending = False

# ✅ 入力エリアを画面下部に配置（送信ボタンを右端に）
with st.container():
    col1, col2 = st.columns([5, 1])  # ✅ 入力エリア (5) : 送信ボタン (1) の比率

    with col1:
        user_input = st.text_input(
            "👤 メッセージを入力:",
            key="user_input",
            value="",
            help="ここに入力して送信",
            label_visibility="collapsed"
        )

    with col2:
        send_button = st.button(
            "送信中…" if st.session_state.sending else "送る",
            use_container_width=True,
            disabled=st.session_state.sending  # ✅ 送信中ならボタンを無効化
        )

# ✅ 送信ボタンが押されたとき
if send_button and user_input and not st.session_state.sending:
    # ✅ 送信中状態に変更（UI を更新）
    st.session_state.sending = True
    st.rerun()  # 🎯 ここでリフレッシュして UI を更新

# ✅ 送信処理（送信ボタンが押されていて、送信中の場合にのみ実行）
if st.session_state.sending:
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

    # ✅ 送信完了後にボタンを再有効化
    st.session_state.sending = False

    # ✅ ページをリフレッシュ
    st.rerun()
