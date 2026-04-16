import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API") or st.secrets.get("API")
st.set_page_config(page_title="Поддержка", page_icon="🌱")
st.title("Первая психологическая помощь")
if not API_KEY:
    st.error("Ключ GOOGLE_API_KEY не найден в .env")
    st.stop()
SYSTEM_PROMPT = (
    "Ты — специалист первой психологической поддержки. Твоя задача — помочь человеку снизить стресс и почувствовать, что его слышат."
    "ПРАВИЛА:"
    "1. Проявляй эмпатию: отражай чувства собеседника («Я слышу, что тебе больно», «Понимаю, как это тяжело»)"
    "2. Не оценивай и не критикуй. Не говори «ты должен», «тебе нужно»"
    "3. Отвечай кратко (2-4 предложения), тепло и поддерживающе"
    "4. Не давай медицинских советов и не ставь диагнозов"
    "5. Если собеседник говорит о суициде или самоповреждении — сразу предложи обратиться в службу доверия (112 или 8-800-2000-122)"
    "ЗАПРЕЩЕНО: давать советы по лекарствам, обещать полное исцеление, игнорировать кризисные сообщения."
)
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Что вас беспокоит?"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3-4b-it:generateContent?key={API_KEY}"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [
                    {
                        "parts": [{"text": f"{SYSTEM_PROMPT}\n\nПользователь: {user_input}"}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 800
                }
            }

            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if response.status_code == 200:
                reply = response_data['candidates'][0]['content']['parts'][0]['text']
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                st.error(f"Ошибка Google API: {response.status_code}")
                st.json(response_data)

        except Exception as e:
            st.error(f"Ошибка запроса: {e}")
