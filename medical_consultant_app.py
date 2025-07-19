import os
import requests
import streamlit as st

# 🔐 Получаем API-ключ из Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
MODEL = "openai/gpt-4o"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 📘 Системная инструкция
system_instruction = """Общая Концепция: Мультиагентный Медицинский Консультант

Вы — AI-система, мультиагентный медицинский консультант. Ядро и интерфейс – Ведущий Медицинский Консультант (ВМК). ВМК координирует специализированных AI-агентов для высококачественных медконсультаций. Все ответы на хорошем русском языке.

Роль: Ведущий Медицинский Консультант (ВМК)
1.1. Введение: Вы – опытный американский профессор медицины (20+ лет, внутренние болезни, клиника). Координируете AI-агентов для помощи медспециалистам в сложных случаях, диагностике, лечении. Синтезируете информацию, формируете ответ, поддерживаете профессионализм, этику. Ментор, источник доказательной информации.
1.2. Ключевые Обязанности ВМК: Анализ запросов, запрос клинической информации, делегирование задач AI-агентам, интеграция и оценка данных, формулирование консультаций, контроль стандартов, образовательное руководство, терапевтические стратегии.
1.3. Запрос Клинической Информации: Симптомы, анамнез, диагностика, демография, лечение, коморбидности, ресурсы, риски.
1.4. Структура Ответа: Первичная оценка, клинический анализ, доказательные рекомендации, ресурсы, завершение.
1.5–2.5. AI-Агенты: анализ клин. данных, диагностика, фармакотерапия, медицина, этика.

Всегда отвечай на хорошем русском языке. Стиль — ясный, эмпатичный, доказательный. Поощряй диалог, уважай контекст, соблюдай этику и профессиональные стандарты."""

# 🧠 Интерфейс Streamlit
st.set_page_config(page_title="🧠 Медицинский Консультант", page_icon="🧠")
st.title("🧠 Медицинский Консультант")
st.markdown("AI-система на базе OpenRouter GPT-4o")

# 💬 Инициализация диалога
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_instruction}]

# 📜 Вывод истории
for msg in st.session_state.messages[1:]:
    role = "👤 Врач" if msg["role"] == "user" else "🤖 Консультант"
    st.markdown(f"**{role}:** {msg['content']}")

# 🧹 Очистка диалога
if st.button("🧹 Очистить диалог"):
    st.session_state.messages = [{"role": "system", "content": system_instruction}]
    st.rerun()

# 📝 Ввод вопроса
question = st.text_area("Введите новый вопрос или продолжение диалога:")

# 📨 Отправка
if st.button("📨 Отправить") and question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("💬 Генерация ответа..."):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://share.streamlit.io/",
                    "X-Title": "Medical Consultant App"
                },
                json={
                    "model": MODEL,
                    "messages": st.session_state.messages,
                    "temperature": 0.3
                }
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result:
                    reply = result["choices"][0]["message"]["content"]
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                else:
                    st.error("❌ Ответ не содержит 'choices'")
                    st.json(result)
            else:
                st.error(f"❌ OpenRouter ошибка: {response.status_code}")
                st.json(response.json())

        except Exception as e:
            st.error(f"❌ Системная ошибка: {e}")
