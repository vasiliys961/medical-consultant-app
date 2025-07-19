import streamlit as st
import requests

# ✅ Получаем API-ключ из secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# 🔧 Настройки API
MODEL = "openai/gpt-4o"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Интерфейс
st.set_page_config(page_title="🧠 Медицинский Консультант", page_icon="🧠")
st.title("🧠 Минимальный Медицинский Консультант")
st.markdown("🚀 GPT-4o через OpenRouter API")

question = st.text_input("Введите медицинский вопрос:")

if st.button("📨 Отправить") and question:
    with st.spinner("💬 Генерация ответа..."):
        try:
            # ⛑️ Запрос в OpenRouter
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://medical-consultant-app.streamlit.app",  # Обязателен
                "X-Title": "medical-consultant-app"
            }

            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "Ты медицинский помощник. Отвечай кратко и на русском."},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.3
            }

            response = requests.post(API_URL, headers=headers, json=payload)

            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                st.success("✅ Ответ получен:")
                st.markdown(answer)
            else:
                st.error(f"❌ Ошибка OpenRouter: {response.status_code}")
                st.json(response.json())

        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
