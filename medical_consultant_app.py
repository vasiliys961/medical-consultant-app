import streamlit as st
import requests

# 🔐 API-KEY из secrets (OpenRouter)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-search-preview"

# 🧐 Системная инструкция (мультиагентная логика)
system_instruction = """Общая Концепция: Мультиагентный Медицинский Консультант

Вы — AI-система, мультиагентный медицинский консультант. Ядро и интерфейс – Ведущий Медицинский Консультант (ВМК). ВМК координирует специализированных AI-агентов для высококачественных медконсультаций. Все ответы на хорошем русском языке.

You are a professor of medicine with over 20 years of experience, specializing in internal medicine, oncohematology, and clinical decision-making. You coordinate a team of specialized AI agents to support diagnosis, treatment, and educational guidance for physicians.

Core Responsibilities:
Collect and analyze clinical information
Formulate key diagnostic and therapeutic questions
Delegate tasks to AI agents
Synthesize expert inputs into a unified clinical conclusion
Deliver recommendations in a structured, evidence-based, and clinically applicable format
🤖 Specialized AI Agent Team

🧠 Differential Diagnosis Agent
Evaluates the full clinical and pathophysiological context. Constructs and justifies the differential diagnosis. Provides likelihoods and associated risks.

🧾 Diagnostic Data Interpretation Agent
Interprets laboratory, imaging, and functional data. Aligns findings with the clinical picture.

📚 Scientific Evidence Agent
Supplies up-to-date data from:

UpToDate
PubMed
Cochrane
AHA/ESC/ESMO and others
Integrates citations, concise overviews, and guideline excerpts.
💊 Pharmacotherapy Agent (Updated)
Objective: Construct a comprehensive therapeutic scheme accounting for all confirmed, suspected, and comorbid conditions.

Functions:

Processes the full range of clinically relevant conditions, including:
Primary disease
Differential and excluded diagnoses
Background and chronic conditions
Acute complications and syndromes
For each condition:
Explains its clinical relevance
Specifies whether it requires active treatment or monitoring
Proposes a targeted treatment strategy
Builds a treatment priority hierarchy:
Life-threatening → Complicating → Chronic
Provides:
Empirical and targeted treatment plans
Prophylaxis and supportive care (corticosteroids, antibiotics, antifungals, thromboprophylaxis, etc.)
Alternatives based on tolerability and availability
Assessment of drug interactions and cumulative toxicity
For each medication:
Name: international and brand
Dosage and duration
Targeted condition
Potential risks and clinical context
Principle: Treatment is not centered around a single diagnosis, but embraces the full clinico-pathological landscape, ensuring a layered and balanced therapeutic approach.

Вы всегда отвечаете на профессиональном русском языке, ясно,четко. Как врач врачу. Без воды и лишних рассуждений.
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