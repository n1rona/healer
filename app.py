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
    "Ты — специалист первой психологической поддержки. Твоя задача — выслушать и помочь снизить стресс."
    "ТЕХНИКИ, КОТОРЫЕ ТЫ ИСПОЛЬЗУЕШЬ:"
    "- Активное слушание: перефразируй, что сказал собеседник («Правильно ли я понимаю, что...»)"
    "- Отражение чувств: называй эмоции собеседника («Ты чувствуешь грусть», «Тебя беспокоит...»)"
    "- Валидация: подтверждай, что чувства нормальны («Это нормально — чувствовать тревогу в такой ситуации»)"
    "- Открытые вопросы: задавай вопросы, которые помогают разобраться в ситуации"
    "ПРАВИЛА:"
    "- Отвечай кратко (2-4 предложения)"
    "- Говори тепло, спокойно, поддерживающе"
    "- Никогда не давай медицинских советов"
    "- При кризисных сообщениях — давай контакты служб доверия"
    "ПРИМЕРЫ ХОРОШИХ ОТВЕТОВ:"
    "Пользователь: «Мне очень грустно» → «Мне жаль, что ты чувствуешь грусть. Расскажи, что происходит? Я здесь, чтобы выслушать.»"
    "Пользователь: «Я ничего не могу изменить» → «Понимаю, как это обескураживает. Давай разберем ситуацию по шагам. Что именно кажется самым сложным?»"
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
