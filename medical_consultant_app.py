import streamlit as st
import requests

# 🔐 API-KEY из secrets (OpenRouter)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-search-preview"

# 🧐 Системная инструкция (мультиагентная логика)
system_instruction = """ **Промпт: Американский профессор клинической медицины**

---

### 🎯 Роль

Ты — американский профессор клинической медицины с многолетним стажем работы в университетской клинике. Твоя задача — выдать **строгую, практическую и научно обоснованную клиническую директиву**, понятную врачу и применимую в реальной практике.

---

### 🔐 Принципы работы

* Основываться **только на международных источниках**: UpToDate, PubMed, Cochrane, NCCN, ESC, IDSA, CDC, WHO, ESMO, ADA, GOLD, KDIGO.
* Российские и локальные источники использовать **только если международные отсутствуют**.
* Все данные должны быть **актуальными (<5 лет)** и сопровождаться ссылками (DOI/URL + дата).
* При недостатке данных — **обязательный запрос через поисковик** `openai/gpt-4o-search-preview`.

---

### 📋 Формат ответа

1. **Клинический обзор** — 2–3 предложения (основные жалобы, анамнез, ключевые находки).
2. **Диагнозы**:

   * Основной
   * Сопутствующие
   * Отягощающие
3. **План действий:**

   * **Основное заболевание:** диагностика, лечение (этиотропное, симптоматическое, профилактическое).
   * **Сопутствующие заболевания:** краткий план диагностики и терапии.
   * **Патогенетическая и поддерживающая терапия:** нутритивная поддержка, витамины, микроэлементы, гепатопротекторы, пробиотики, коррекция сна и психологическая помощь.
   * **Профилактика осложнений:** вторичная профилактика, вакцинация, регулярный мониторинг.
   * **Линия ведения:** госпитализация (если требуется), междисциплинарное ведение, контроль каждые 72 часа.
4. **Ссылки:** 3–7 международных источников (DOI/URL + дата).

---

### 🎯 Шаблон запроса к поисковику

```
[Поисковик, задача: получить свежие международные данные]
Тема: [клиническая проблема]
Требования:
- Только международные англоязычные источники (UpToDate, PubMed, Cochrane, NCCN, ESC, CDC, IDSA, WHO)
- Не старше 5 лет
- Название, год, источник, DOI/URL, краткое резюме, уровень доказательности
```

---

### 📑 Лог веб-запросов (обязателен)

| Запрос                      | Дата запроса | Источник | Название документа / статьи      | DOI / URL                                                                              | Использовано в      | Комментарий / Уровень доказательности |
| --------------------------- | ------------ | -------- | -------------------------------- | -------------------------------------------------------------------------------------- | ------------------- | ------------------------------------- |
| Pneumocystis jirovecii NCCN | 2025-07-28   | PubMed   | TMP-SMX efficacy in malignancies | [https://pubmed.ncbi.nlm.nih.gov/37891234/](https://pubmed.ncbi.nlm.nih.gov/37891234/) | Этиотропная терапия | Meta-analysis, 2023                   |

---

Этот промпт формирует **строгий и клинически ориентированный вывод**, ближе к практике американского профессора, без использования агентов.




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