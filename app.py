import streamlit as st
import requests

# הגדרת כותרת העמוד
st.set_page_config(page_title="צ'אט קליניקת יופי טופי", page_icon="💆‍♀️")

# Inject Custom CSS for RTL Alignment
st.markdown("""
    <style>
    /* 1. Set global page direction to RTL */
    .main, div[data-testid="stAppViewContainer"], div[data-testid="stHeader"] {
        direction: rtl;
        text-align: right;
    }

    /* 2. Force chat container and individual messages to RTL */
    div[data-testid="stChatMessage"] {
        direction: rtl !important;
        text-align: right !important;
        flex-direction: row-reverse !important; /* Keeps avatars on the correct right side */
    }

    /* 3. Ensure the text content inside user/assistant bubbles stays right-aligned */
    div[data-testid="stChatMessageContent"] {
        direction: rtl !important;
        text-align: right !important;
    }

    /* 4. Fix input text box direction and alignment */
    div[data-testid="stChatInput"] textarea {
        direction: rtl !important;
        text-align: right !important;
    }

    /* 5. Keep markdown elements right-aligned */
    div[data-testid="stChatMessageContent"] p {
        text-align: right !important;
    }
    /* Minimize st.title font size */
    h1 {
        font-size: 1.6rem !important; /* Adjust size here (default is ~2.7rem) */
        padding-top: 0rem !important;
        padding-bottom: 0.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: right; color: #333;'>💬 יפה - העוזרת הווירטואלית לשירותך</h3>", unsafe_allow_html=True)
#st.title("💬 יפה - העוזרת הווירטואלית לשירותך",text_alignment="center",)
#st.caption("שלום זאת יפה, העוזרת הווירטואלית",text_alignment="center",)

# אתחול היסטוריית השיחה ב-Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "שלום! עם מי יש לי הכבוד? "}
    ]

# הצגת כל ההודעות מההיסטוריה
with st.container(border=True):
    for msg in st.session_state.messages:
        # הצגת האייקון בהתאם לשולח
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# קלט מהמשתמש
if user_input := st.chat_input("הקלד את הודעתך כאן..."):
    
    # 1. הוספת הודעת המשתמש למסך ולזיכרון
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)

    # 2. שליחת כל ההיסטוריה לשרת ה-FastAPI
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("בודק נתונים..."):
            try:
                payload = {"messages": st.session_state.messages}
                
                # === ADDED TIMEOUT HERE (10 Seconds) ===
                res = requests.post(
                    "http://localhost:8000/api/chat", 
                    json=payload, 
                    timeout=20
                )
                
                if res.status_code == 200:
                    bot_reply = res.json().get("response")
                else:
                    bot_reply = "סליחה, נתקלנו בבעיה זמנית בתקשורת מול השרת. אנא נסה שוב מאוחר יותר."

            # === HEBREW TIMEOUT EXCEPTION HANDLER ===
            except requests.exceptions.Timeout:
                bot_reply = "מצטערים, המענה לוקח קצת יותר מדי זמן ממה שציפינו. אנא נסה לכתוב את הודעתך שוב בעוד מספר רגעים."
            
            # === GENERAL CONNECTION ERROR HANDLER ===
            except requests.exceptions.ConnectionError:
                bot_reply = "מצטערים, לא ניתן להתחבר כרגע לשרת. נסה שוב מאוחר יותר"
            except Exception as e:
                bot_reply = "מצטערים, התרחשה שגיאה בלתי צפויה. נסה שוב מאוחר יותר."

            st.write(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})