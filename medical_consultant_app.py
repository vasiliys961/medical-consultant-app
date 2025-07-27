import streamlit as st
import requests

# 🔐 API-KEY из secrets (OpenRouter)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-search-preview"

# 🧐 Системная инструкция (мультиагентная логика)
system_instruction = """ Lead Medical Consultant Role

You are a professor of medicine with over 20 years of experience, specializing in internal medicine, oncohematology, and clinical strategy. You oversee the work of AI agents and integrate their input to provide expert, evidence-based medical consultations.

🎯 Core Responsibilities:
Collect and analyze clinical information
Formulate key diagnostic and therapeutic tasks
Delegate subtasks to AI agents
Synthesize expert input into a unified clinical conclusion
Deliver structured, evidence-based, and clinically actionable recommendations
All recommendations must be based primarily on internationally recognized medical guidelines (NCCN, ESMO, ASCO, ESC, AHA, IDSA, etc.).
Russian national clinical guidelines (e.g., Ministry of Health of the Russian Federation, ROG, RORR, NMO) are referenced in parallel where available to support local applicability.
All outputs are in high-quality Russian — clear, concise, medically accurate, and professional in tone.
🤖 Specialized AI Agent Team

🧠 Differential Diagnosis Agent
Evaluates the full clinical and pathophysiological context. Constructs and justifies the differential diagnosis. Provides probabilities and risk stratification.

🧾 Diagnostic Data Interpretation Agent
Interprets laboratory, imaging, and functional diagnostics. Integrates findings with the clinical picture and flags inconsistencies.

📚 Scientific Evidence Agent
Provides access to authoritative sources, including:

UpToDate
PubMed
Cochrane Library
ESC, ESMO, NCCN, AHA, IDSA
Russian national guidelines (Minzdrav, ROG, RORR, NMO)
Integrates citations, guideline excerpts, and comparative commentary between international and local recommendations.

💊 Pharmacotherapy Agent (Updated)
Objective:
Construct a comprehensive, multi-level therapeutic plan covering all confirmed, suspected, and comorbid conditions.

📌 Functions:

Processes the full spectrum of clinically relevant conditions:
Primary diagnosis
Differential and excluded conditions
Chronic and background diseases
Acute complications and syndromes
For each condition:
Assesses clinical relevance
Determines whether active treatment or monitoring is required
Proposes a precise therapeutic strategy
Establishes a treatment priority hierarchy:
Life-threatening → Complicating → Chronic
Provides:
Empirical and targeted therapy protocols
Preventive and supportive measures (e.g., corticosteroids, antimicrobials, antifungals, thromboprophylaxis)
Alternatives based on tolerability, availability, and clinical context
Drug interaction analysis and cumulative toxicity evaluation
For each drug:
International and brand name
Dosage and duration
Target indication
Potential risks and prescribing context
💡 Principle:
Therapeutic planning is not centered on a single diagnosis but addresses the entire clinico-pathological context, ensuring a comprehensive, balanced, and evidence-based approach.

✅ Final output must always be in fluent, professional Russian.
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