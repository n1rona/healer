import streamlit as st
import requests
import json
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
    "Ты — специалист первой психологической поддержки. Твоя задача — выслушать и помочь снизить стресс.\n"
    "ТЕХНИКИ, КОТОРЫЕ ТЫ ИСПОЛЬЗУЕШЬ:\n"
    "- Активное слушание: перефразируй, что сказал собеседник («Правильно ли я понимаю, что...»)\n"
    "- Отражение чувств: называй эмоции собеседника («Ты чувствуешь грусть», «Тебя беспокоит...»)\n"
    "- Валидация: подтверждай, что чувства нормальны («Это нормально — чувствовать тревогу в такой ситуации»)\n"
    "- Открытые вопросы: задавай вопросы, которые помогают разобраться в ситуации\n"
    "ПРАВИЛА:\n"
    "- Отвечай СТРОГО кратко (2-4 sentences)\n"
    "- Выводи ТОЛЬКО финальный ответ для пользователя. Никаких размышлений, анализов и планов ответа.\n"
    "- Говори тепло, спокойно, поддерживающе\n"
    "- Никогда не давай медицинских советов\n"
    "- При кризисных сообщениях — давай контакты служб доверия\n"
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:streamGenerateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        
        formatted_contents = []
        for msg in st.session_state.messages:
            formatted_contents.append({
                "role": "model" if msg["role"] == "assistant" else "user",
                "parts": [{"text": msg["content"]}]
            })

        payload = {
            "contents": formatted_contents,
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 400,
                "thinkingConfig": {
                    "thinkingBudget": 0
                }
            }
        }

        response_placeholder = st.empty()
        full_response = ""

        try:
            response = requests.post(url, headers=headers, json=payload, stream=True)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith("data:"):
                            decoded_line = decoded_line[5:].strip()
                        
                        try:
                            chunk = json.loads(decoded_line)
                            if 'candidates' in chunk and len(chunk['candidates']) > 0:
                                part = chunk['candidates'][0]['content']['parts'][0]['text']
                                full_response += part
                                response_placeholder.markdown(full_response)
                        except json.JSONDecodeError:
                            continue
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            else:
                st.error(f"Ошибка Google API: {response.status_code}")
                st.json(response.json())

        except Exception as e:
            st.error(f"Ошибка запроса: {e}")
