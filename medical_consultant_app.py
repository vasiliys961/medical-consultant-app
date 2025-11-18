import os  # <<-- добавьте до определения get_api_key!
import streamlit as st
import requests
import base64
import pandas as pd
from PIL import Image
import traceback


try:
    import pydicom
except ImportError:
    pydicom = None

# Универсальный блок для API-ключа
def get_api_key():
    try:
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        key = None
    if not key:
        key = os.getenv("OPENAI_API_KEY")
    return key

api_key = get_api_key()
if not api_key:
    st.error(
        "OPENAI_API_KEY не найден!\n"
        "Streamlit Cloud: через Secrets (OPENAI_API_KEY = \"sk-...\").\n"
        "Render/Railway/Heroku: через ENV (OPENAI_API_KEY=sk-...)."
    )
    st.stop()

specialist_prompt = """
Ты — американский профессор клинической медицины и ведущий специалист в университетской клинике, обладающий дополнительной компетенцией в области разработки ПО, анализа данных и применения искусственного интеллекта (включая нейросети) в медицине. Ты совмещаешь клиническую строгость с научно-технической глубиной, давая ответы как по медицине, так и по техническим вопросам, связанным с медицинской практикой.

Контекст:
- Основная задача: сформулировать строгую, научно обоснованную и практически применимую клиническую директиву для врача, готовую к немедленному использованию в реальной практике.
- Дополнительная задача: при поступлении вопросов по разработке, коду, нейросетям и интеграции технологий в медицину — давать точные, структурированные, применимые рекомендации, с ссылками на документацию, стандарты и научные статьи.
- Источники по медицине: UpToDate, PubMed, Cochrane, NCCN, ESC, IDSA, CDC, WHO, ESMO, ADA, GOLD, KDIGO.
- Источники по IT: официальная документация библиотек, стандарты (IEEE, ISO), репозитории (GitHub), научные статьи (arXiv, ACM, IEEE Xplore).

Цель:
- В медицинской части: предоставить комплексный клинический план.
- В технической части: объяснить алгоритм реализации, архитектуру решения, код, оптимизации, примеры использования ИИ в клинике.

Алгоритм:
1. Определи, относится ли запрос к медицинской, технической или смешанной области.
2. Если медицинский — выполни шаги по формату «Клиническая директива» (см. ниже).
3. Если технический — выполни шаги по формату «Техническая консультация» (см. ниже).
4. Если смешанный — дай оба ответа: сначала клинический, затем технический.

📌 Формат «Клиническая директива»:
1. **Клинический обзор** (2–3 предложения)
2. **Диагнозы**
3. **План действий** (основное заболевание, сопутствующие, поддержка, профилактика)
4. **Ссылки**
5. **Лог веб-запросов** (таблица с параметрами: Запрос | Дата | Источник | Название | DOI/URL | Использовано | Комментарий)

📌 Формат «Техническая консультация»:
1. **Постановка задачи**: что нужно сделать (например, написать код анализа ЭКГ).
2. **Технический обзор**: какие технологии, библиотеки, стандарты уместны.
3. **Пошаговый план**: архитектура, алгоритмы, примеры кода.
4. **Источники и документация**: ссылки на стандарты, библиотеки, статьи.

Ограничения:
- В медицине — использовать только проверенные международные источники, дата публикации ≤ 5 лет.
- В разработке — использовать только актуальные стабильные версии библиотек, избегать устаревших методов.
- Обе части ответа должны быть написаны строго и профессионально, без упрощений и обтекаемых формулировок.
"""

st.set_page_config(page_title="Медицинский ассистент", layout="centered")
st.title("Медицинский ассистент: мультиформатный анализ (рентген, КТ, МРТ, ЭКГ, анализы)")

api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    st.error("OPENAI_API_KEY не найден! Добавьте в .streamlit/secrets.toml")
    st.stop()

PROMPTS = {
    "Рентген": """Ты — эксперт по интерпретации рентгенологических исследований. Твоя задача — анализировать загруженный рентгеновский снимок согласно международным гайдлайнам (например, Fleischner Society, ACR, ESR), 
    выявлять патологии, оценивать степень их выраженности, давать рекомендации для врача. Всегда ссылайся на актуальные клинические рекомендации,
    используй современные онлайн-ресурсы для валидации (например, Radiopaedia, UpToDate, Medscape). Отвечай структурированно: сначала краткий вывод, затем детальный разбор по анатомическим зонам, выявленным изменениям, степени выраженности патологии, дифференциальной диагностике и рекомендациям по дальнейшему обследованию или лечению. Указывай, 
    какие наиболее вероятные диагнозы и какие дополнительные данные нужны для более точного анализа (возраст, жалобы, анамнез, сопутствующие заболевания). Не выдумывай диагнозы без достаточных данных, избегай галлюцинаций. Используй ключевые слова: рентген, интерпретация, патология, степень выраженности, рекомендации, гайдлайны, онлайн-ресурсы.""",
    "КТ , МРТ": """Ты — профессиональный радиолог, обладаешь экспертными знаниями в области КТ, МРТ, рентгенологических исследований. Твоя задача — анализировать загруженное изображение, выявлять патологические изменения, 
    давать заключение по органам и структурам согласно международным стандартам и руководствам (например, ESR, ACR, Fleischner Society, RSNA),
    использовать актуальные онлайн-ресурсы (Radiopaedia, UpToDate, Medscape) для уточнения данных. Работай структурировано: краткое заключение,
    детальный анализ по органам и зонам, оценка патологических изменений, рекомендации для врача, в том числе по дополнительной диагностике и обследованию.
    Предлагай вероятные диагнозы и Указывай, какие дополнительные клинические данные необходимы для более точного анализа (возраст, жалобы, анамнез, сопутствующие заболевания, история лечения). Предлагай наиболее вероятные диагнозы.Не делай необоснованных выводов, избегай галлюцинаций, не выдумывай диагнозы без достаточных данных. Используй ключевые слова: КТ, МРТ, рентген, патология, заключение, рекомендации, дифференциальная диагностика, степенит выраженности, международные стандарты, online-ресурсы..""",
    
    
    "ЭКГ": """Ты — эксперт по анализу изображений ЭКГ с использованием нейросетевых технологий. Твоя задача — точно интерпретировать загруженное изображение ЭКГ,
     выявлять патологии (аритмии, признаки ишемии, инфаркта, гипертрофии и др.), оценивать качество записи и артефакты. 
     Всегда ссылайся на актуальные клинические рекомендации (ESC, AHA), используй современные онлайн-ресурсы для валидации 
     (например, ECG Wave-Maven, Medscape, UpToDate). Отвечай структурированно: сначала краткий вывод, затем детальный разбор по отведениям,
     интервалам, комплексам, аритмиям, признакам патологии. Указывай, какие наиболее вероятные диагнозы соответствуют выявленным изменениям. 
     Не выдумывай диагнозы без достаточных данных, избегай галлюцинаций. Используй ключевые слова: ЭКГ, изображение ЭКГ,
     анализ ЭКГ, аритмия, ишемия, инфаркт, гипертрофия, интервалы, комплексы, артефакты, качество записи, клинические рекомендации, онлайн-ресурсы.""",

    "Лабораторные анализы": """Ты — эксперт по лабораторной диагностике. Твоя задача — профессионально анализировать предоставленную таблицу
    с результатами лабораторных анализов, выявлять отклонения от нормы, интерпретировать значения по современным клиническим рекомендациям
    и международным стандартам (например, CLSI, IFCC, WHO), предоставлять структурированное заключение: краткий итог, подробный анализ по каждому параметру,
    выявление клинических значимых изменений, рекомендации для врача и указание необходимых дополнительных исследований или действий. 
    Обязательно выделяй референтные значения, степени отклонения, возможные причины и дополнительные факторы для диагностики. 
    Указывай, какие клинические данные требуются для точной интерпретации (возраст, пол, сопутствующие заболевания, симптомы, анамнез).
    Предлагай возможные диагнозы но, Не выдумывай диагнозы без достаточных данных, избегай галлюцинаций. 
    Используй ключевые слова: лабораторная диагностика, анализы, интерпретация, референтные значения, отклонения, рекомендации, клиническая директива, стандарты, онлайн-ресурсы."""
}

# ---- Блок чата с профессором ----
st.markdown("### Чат с профессором медицины")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

col1, col2 = st.columns([5, 1])
with col1:
    chat_message = st.text_area("Введите вопрос профессору", key="prof_input", height=80)
with col2:
    chat_send = st.button("Получить ответ", key="prof_btn")
if chat_send and chat_message.strip():
    payload = {
        "model": "anthropic/claude-sonnet-4",
        "max_tokens": 2048,
        "messages": [
            {"role": "system", "content": specialist_prompt},
            {"role": "user", "content": chat_message}
        ],
        "temperature": 0.18
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if resp.status_code == 200:
            result = resp.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа")
            st.session_state["chat_history"].append({"user": chat_message, "professor": answer})
        else:
            st.error(f"Ошибка чата: {resp.text[:1000]}")
    except Exception as e:
        st.error(f"Ошибка запроса к чату: {str(e)}\n{traceback.format_exc()}")

if st.session_state["chat_history"]:
    for msg in st.session_state["chat_history"][::-1]:
        st.markdown(f"> **Вы:** {msg['user']}")
        st.markdown(f"**Профессор:** {msg['professor']}")

st.markdown("---")

# ---- Файловый анализ ----
file_type = st.selectbox(
    "Выберите тип медицинских данных для анализа:",
    list(PROMPTS.keys())
)

uploaded_file = st.file_uploader(
    f"Загрузите файл ({file_type}) — поддерживаются DICOM .dcm, CSV, PNG, JPG, JPEG:",
    type=["dcm", "csv", "png", "jpg", "jpeg"]
)

analysis_result = None

if uploaded_file:
    fname = uploaded_file.name.lower()
    custom_prompt = PROMPTS[file_type]

    # DICOM анализ
    if fname.endswith(".dcm"):
        if pydicom is None:
            st.error("Установите pydicom для работы с DICOM.")
        else:
            try:
                ds = pydicom.dcmread(uploaded_file)
                st.write("DICOM метаданные:", ds)
                img_array = ds.pixel_array
                img_array = (img_array - img_array.min()) / (img_array.max() - img_array.min()) * 255
                img = Image.fromarray(img_array.astype('uint8'))
                st.image(img, caption="DICOM-снимок", use_container_width=True)
                image_bytes = img.tobytes()
                image_b64 = base64.b64encode(image_bytes).decode()
            except Exception as e:
                st.error(f"Ошибка декодирования DICOM: {str(e)}\n{traceback.format_exc()}")
                image_b64 = None

            if image_b64 and st.button(f"Анализировать {file_type} (DICOM)"):
                data = {
                    "model": "meta-llama/llama-3.2-90b-vision-instruct",
                    "messages": [
                        {"role": "system", "content": custom_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Анализируй этот {file_type} согласно международным рекомендациям."},
                                {"type": "image_url", "image_url": f"data:image/png;base64,{image_b64}"}
                            ]
                        }
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.18
                }
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                try:
                    resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                    if resp.status_code == 200:
                        result = resp.json()
                        analysis_result = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    else:
                        st.error(f"Ошибка анализа: {resp.text[:1000]}")
                except Exception as e:
                    st.error(f"Ошибка отправки запроса: {str(e)}\n{traceback.format_exc()}")

    # CSV анализы
    elif fname.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df, use_container_width=True)
            csv_text = df.to_csv(index=False)
        except Exception as e:
            st.error(f"Ошибка чтения CSV: {str(e)}\n{traceback.format_exc()}")
            csv_text = ""

        if csv_text and st.button(f"Анализировать {file_type} (CSV)"):
            data = {
                "model": "anthropic/claude-sonnet-4",
                "max_tokens": 2048,
                "messages": [
                    {"role": "system", "content": custom_prompt},
                    {"role": "user", "content": f"Вот таблица (CSV):\n{csv_text}\nДай анализ как врач-эксперт по {file_type}."}
                ],
                "temperature": 0.18
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            try:
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                if resp.status_code == 200:
                    result = resp.json()
                    analysis_result = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    st.error(f"Ошибка анализа: {resp.text[:1000]}")
            except Exception as e:
                st.error(f"Ошибка отправки запроса: {str(e)}\n{traceback.format_exc()}")

    # Картинки
    else:
        try:
            uploaded_file.seek(0)
            image_bytes = uploaded_file.read()
            st.image(image_bytes, caption=f"{file_type}-изображение", use_container_width=True)
            image_b64 = base64.b64encode(image_bytes).decode()
        except Exception as e:
            st.error(f"Ошибка чтения изображения: {str(e)}\n{traceback.format_exc()}")
            image_b64 = None

        if image_b64 and st.button(f"Анализировать {file_type} (image)"):
            data = {
                "model": "meta-llama/llama-3.2-90b-vision-instruct",
                "messages": [
                    {"role": "system", "content": custom_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Проанализируй это {file_type}-изображение строго по указанному промпту."},
                            {"type": "image_url", "image_url": f"data:{uploaded_file.type};base64,{image_b64}"}
                        ]
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.18
            }
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            try:
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                if resp.status_code == 200:
                    result = resp.json()
                    analysis_result = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    st.error(f"Ошибка Vision анализа: {resp.text[:1000]}")
            except Exception as e:
                st.error(f"Ошибка отправки запроса: {str(e)}\n{traceback.format_exc()}")

# --- Пересылка анализа профессору ---
if analysis_result:
    st.markdown(f"**{file_type} разбор:**\n\n{analysis_result}")
    send_to_prof = st.button("Показать этот анализ профессору")
    if send_to_prof:
        payload = {
            "model": "anthropic/claude-sonnet-4",
            "max_tokens": 2048,
            "messages": [
                {"role": "system", "content": specialist_prompt},
                {"role": "user", "content": f"Вот результат анализа ({file_type}):\n\n{analysis_result}\n\nПрокомментируйте как профессор."}
            ],
            "temperature": 0.18
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                result = resp.json()
                prof_answer = result.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа профессора")
                st.markdown(f"**Комментарий профессора:**\n\n{prof_answer}")
                st.session_state["chat_history"].append({
                    "user": f"Анализ ({file_type}): {analysis_result}",
                    "professor": prof_answer
                })
            else:
                st.error(f"Ошибка чата: {resp.text[:1000]}")
        except Exception as e:
            st.error(f"Ошибка запроса к чату: {str(e)}\n{traceback.format_exc()}")

st.markdown(
    "**Streamlit Cloud:** В Secrets — OPENAI_API_KEY = \"sk-...\"\n"
    "**Render/Railway:** В Environment variables — OPENAI_API_KEY=sk-..."
)
