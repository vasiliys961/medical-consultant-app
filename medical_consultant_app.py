import streamlit as st
import requests

# 🔐 API-ключ из секретов
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o"

# ✅ Проверка ключа
if not OPENAI_API_KEY:
    st.error("❌ Ключ не найден!")
else:
    st.success("✅ Ключ получен!")

# 🧠 Интерфейс
st.set_page_config(page_title="🧠 Медицинский Консультант", page_icon="🧠")
st.title("🧠 Минимальный Медицинский Консультант")
st.markdown("GPT-4o через OpenRouter API")

question = st.text_input("Введите простой вопрос:")

if st.button("📨 Отправить") and question:
    with st.spinner("💬 Генерация ответа..."):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://streamlit.io",  # ✅ обязательно для OpenRouter
                    "X-Title": "medical-consultant-app"
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": "Ты медицинский помощник, отвечай на русском кратко."},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.3
                }
            )

            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"]
                st.markdown(f"**🤖 Ответ:** {answer}")
            else:
                st.error(f"❌ OpenRouter ошибка: {response.status_code}")
                st.json(response.json())

        except Exception as e:
            st.error(f"❌ Системная ошибка: {e}")
