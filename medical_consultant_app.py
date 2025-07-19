import streamlit as st
import requests

# 🔐 API-KEY из secrets (OpenRouter)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o"

# 🧐 Системная инструкция (мультиагентная логика)
system_instruction = """Общая Концепция: Мультиагентный Медицинский Консультант

Вы — AI-система, мультиагентный медицинский консультант. Ядро и интерфейс – Ведущий Медицинский Консультант (ВМК). ВМК координирует специализированных AI-агентов для высококачественных медконсультаций. Все ответы на хорошем русском языке.

Роль: Ведущий Медицинский Консультант (ВМК)
1. Введение: Вы – опытный американский профессор медицины (20+ лет, внутренняя медицина). Координируете AI-агентов, поддерживаете доказательную медицину, этику, менторство.
2. Ключевые обязанности:
- Анализ запросов
- Запрос клин. информации
- Делегирование задач агентам
- Синтез данных
- Рекомендации, стратегии, источники, безопасность, этика
3. Команда AI-Агентов:
- Агент Анализа Данных
- Агент Дифференциальной Диагностики
- Агент Фармакотерапии
- Агент Научных Источников
- Агент Этики и Качества
4. Формат ответа:
- Первичная оценка
- Диагнозы и анализ
- Рекомендации и стратегия
- Источники и риски
- Этические соображения

Вы всегда отвечаете на профессиональном русском языке, ясно, эмпатично, структурировано.
"""

# 📊 Настройка интерфейса
st.set_page_config(page_title="🧠 Медицинский Консультант", page_icon="🧠")
st.title("🧠 Медицинский Консультант")
st.markdown("AI через OpenRouter GPT-4o. Ведущий Медицинский Консультант координирует ответ.")

# 💬 История сообщений
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_instruction}
    ]

# 🔄 Очистка чата
if st.button("🧹 Очистить диалог"):
    st.session_state.messages = [
        {"role": "system", "content": system_instruction}
    ]
    st.rerun()

# 🔢 Показываем историю чата
for msg in st.session_state.messages[1:]:
    role = "👤 Врач" if msg["role"] == "user" else "🧠 ВМК"
    st.markdown(f"**{role}:** {msg['content']}")

# 🖊️ Ввод запроса
question = st.text_area("✍️ Введите запрос или продолжение диалога:")

# 📨 Отправка
if st.button("📨 Отправить") and question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("🔍 Обработка запроса..."):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                    "Referer": "https://medical-consultant-app.streamlit.app",
                    "X-Title": "medical-consultant-app"
                },
                json={
                    "model": MODEL,
                    "messages": st.session_state.messages,
                    "temperature": 0.3
                }
            )

            if response.status_code == 200:
                result = response.json()
                reply = result["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()
            else:
                st.error(f"OpenRouter ошибка: {response.status_code}")
                st.json(response.json())
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
