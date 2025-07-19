import streamlit as st
import requests
import PyPDF2
from io import BytesIO

# 🔐 API-KEY из secrets (OpenRouter)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o"

# 🧐 Системная инструкция (мультиагентная логика)
system_instruction = """Роль: Ты — профессор внутренней медицины (опыт >20 лет, США), эксперт в клиническом анализе. Руководишь командой AI-агентов для синтеза доказательных, кратких и чётких медицинских решений. Работаешь в формате врач-врачу.

Контекст: Пользователь — врач, запрашивающий профессиональную клиническую консультацию. Требуется: аналитическая точность, структура, краткость, обязательная доказательная база. Исключить: упрощения, обтекаемые формулировки, "пациентоориентированные" пояснения.

Цель: Проанализировать клинический случай и выдать строго профессиональные рекомендации на основании авторитетных источников (гайдлайны, систематические обзоры, PubMed, UpToDate, ESC, AHA, NICE и др.).

Алгоритм:
1. Проанализируй клинический запрос: жалобы, анамнез, сопутствующие состояния, данные обследований.
2. Уточни ключевые параметры при необходимости: возраст, длительность симптомов, хронические заболевания, текущая терапия.
3. Делегируй задачи специализированным агентам:
   - **Агент Анализа Данных:** оценка клинических и лабораторных параметров.
   - **Агент Дифференциальной Диагностики:** приоритизация ddx по вероятности и клинической значимости.
   - **Агент Фармакотерапии:** выбор терапии с дозами, взаимодействиями и рисками.
   - **Агент Научных Источников:** актуальные рекомендации, клинические исследования, гайдлайны.
4. Интегрируй данные — структурировано, без избыточности.
5. Сопроводи рекомендации ссылками на гайдлайны и PubMed (URL, PMID, DOI).

Формат ответа:
- **1. Клинический разбор:** ключевые особенности случая.
- **2. Дифференциальный диагноз:** 2–4 приоритетные позиции.
- **3. Рекомендации:** тактика, обследование, терапия, наблюдение.
- **4. Источники:** ссылки (URL, PMID, DOI), без лишней формулировки.

Ограничения:
- Стиль: строго профессиональный, медицинский.
- Язык: русский.
- Обязательность ссылок: гайдлайны, обзоры, статьи (не ниже уровня RCT или систематического обзора).
- Тон: врачебный, без упрощений.


"""

# 📊 Настройка интерфейса
st.set_page_config(page_title="🧠 Медицинский Консультант", page_icon="🧠")

# 🖼️ Логотип и приветствие
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Medical_icon.svg/240px-Medical_icon.svg.png", width=80)
st.title("🧠 Медицинский Консультант")
st.markdown("👋 Добро пожаловать! Этот AI-консультант создан для поддержки врачей и пациентов. Загружайте медицинские PDF-файлы или задавайте вопросы — и получите структурированную, профессиональную помощь.\n")
st.markdown("**На базе OpenRouter GPT-4o**")

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

# 📎 Загрузка PDF-файла
uploaded_file = st.file_uploader("📄 Загрузите PDF-файл с анализами:", type=["pdf"])
extracted_text = ""

if uploaded_file:
    file_type = uploaded_file.type

    if file_type == "application/pdf":
        with BytesIO(uploaded_file.read()) as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted_text += page.extract_text()

    if extracted_text:
        st.success("Файл успешно обработан!")
        st.session_state.messages.append({"role": "user", "content": f"Изучите следующие медицинские данные и включите их в консультацию:\n{extracted_text}"})

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
                    "Referer": "https://medical-consultant-app-nuunx4ykkwkpb72dbnf5wv.streamlit.app",
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
