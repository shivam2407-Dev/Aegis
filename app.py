import re
import streamlit as st
from gliner import GLiNER
from transformers import pipeline as hf_pipeline

st.set_page_config(
    page_title="PII Redactor",
    page_icon="🔒",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e8f0;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 10%, #1a0a2e 0%, #0a0a0f 50%),
                radial-gradient(ellipse at 80% 90%, #0a1a1f 0%, transparent 60%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none; }

.block-container {
    max-width: 1100px !important;
    padding: 3rem 2rem !important;
}

h1.title {
    font-family: 'Space Mono', monospace;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #c084fc 0%, #67e8f9 60%, #a5f3fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

p.subtitle {
    font-size: 1rem;
    color: #6b7280;
    font-weight: 300;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 3rem;
}

.stTextArea textarea {
    background: #111118 !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 1rem !important;
    resize: vertical !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #c084fc !important;
    box-shadow: 0 0 0 3px rgba(192, 132, 252, 0.1) !important;
}
.stTextArea label { color: #9ca3af !important; font-size: 0.8rem !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.75rem 2.5rem !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
}

.result-box {
    background: #111118;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    line-height: 1.7;
    color: #e8e8f0;
    min-height: 120px;
    word-break: break-word;
}

.result-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #4b5563;
    margin-bottom: 0.6rem;
}

.tag {
    display: inline-block;
    background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(8,145,178,0.25));
    border: 1px solid rgba(192,132,252,0.4);
    color: #c084fc;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    letter-spacing: 0.05em;
}

.entity-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #1a1a27;
    border: 1px solid #2a2a3a;
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    margin: 0.25rem;
    font-size: 0.85rem;
}
.entity-chip .etype {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: #c084fc;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.entity-chip .evalue {
    color: #f87171;
    font-weight: 500;
}
.entity-chip .escore {
    color: #4b5563;
    font-size: 0.7rem;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a2a3a, transparent);
    margin: 2.5rem 0;
}

.stat-row {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}
.stat {
    background: #111118;
    border: 1px solid #2a2a3a;
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    text-align: center;
    flex: 1;
}
.stat-num {
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #c084fc;
}
.stat-label {
    font-size: 0.7rem;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.stSpinner > div { border-top-color: #c084fc !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_models():
    g = GLiNER.from_pretrained("knowledgator/gliner-pii-small-v1.0")
    c = hf_pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return g, c

PII_LABELS = [
    "person name", "email address", "phone number",
    "password or secret value", "api key or token",
    "id number or reference number", "credit card number",
    "social security number", "date of birth", "ip address",
    "username", "passport number", "bank account number",
]
LOC_LABELS  = ["location", "country", "city", "region"]
THRESHOLD   = 0.4

_EMAIL_RE          = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
_INFORMAL_SECRET_RE = re.compile(r'(?i)\b(pass|password|passwd|secret|token|key)\s+([A-Za-z0-9@#$!%^&*]{4,})')


def _is_personal_location(classifier, text, location):
    result = classifier(
        f'In the sentence "{text}", the place "{location}" is',
        candidate_labels=[
            "where the speaker personally lives, is from, or was born",
            "a travel destination, business location, or general reference",
        ],
    )
    return result["labels"][0] == "where the speaker personally lives, is from, or was born"


def _resolve_overlaps(entities):
    resolved, last_end = [], -1
    for e in sorted(entities, key=lambda x: (x["start"], -x["score"])):
        if e["start"] >= last_end:
            resolved.append(e)
            last_end = e["end"]
    return resolved


def _apply_redaction(text, entities):
    result, cursor = "", 0
    for e in sorted(entities, key=lambda x: x["start"]):
        result += text[cursor:e["start"]] + f'<span class="tag">{e["label"].upper().replace(" ", "_")}</span>'
        cursor  = e["end"]
    return result + text[cursor:]


def redact_text(gliner, classifier, text):
    pii  = gliner.predict_entities(text, PII_LABELS, threshold=THRESHOLD)
    locs = gliner.predict_entities(text, LOC_LABELS, threshold=THRESHOLD)
    sens_locs = [{**e, "label": "personal location"} for e in locs if _is_personal_location(classifier, text, e["text"])]

    fallback = []
    for m in _EMAIL_RE.finditer(text):
        fallback.append({"label": "email address", "text": m.group(), "start": m.start(), "end": m.end(), "score": 1.0})
    for m in _INFORMAL_SECRET_RE.finditer(text):
        fallback.append({"label": "password or secret value", "text": m.group(2), "start": m.start(2), "end": m.end(2), "score": 1.0})

    all_entities = _resolve_overlaps(pii + sens_locs + fallback)
    return {
        "redacted_html": _apply_redaction(text, all_entities),
        "redacted_text": _apply_redaction(text, all_entities).replace('<span class="tag">', "<").replace("</span>", ">"),
        "entities": [{"type": e["label"], "value": e["text"], "score": round(e["score"], 2)} for e in all_entities],
    }


# ── UI ────────────────────────────────────────────────────────────────────────

st.markdown('<h1 class="title">PII Redactor</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Semantic sensitive data detection & redaction</p>', unsafe_allow_html=True)

with st.spinner("Loading models..."):
    gliner, classifier = load_models()

user_input = st.text_area("Input text", placeholder="Enter text containing sensitive information...", height=150, label_visibility="collapsed")

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    run = st.button("REDACT →")

if run and user_input.strip():
    with st.spinner("Analyzing..."):
        result = redact_text(gliner, classifier, user_input.strip())

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="result-label">Redacted Output</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{result["redacted_html"]}</div>', unsafe_allow_html=True)

    n = len(result["entities"])
    types = len(set(e["type"] for e in result["entities"]))
    avg_score = round(sum(e["score"] for e in result["entities"]) / n, 2) if n else 0

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat"><div class="stat-num">{n}</div><div class="stat-label">Entities Found</div></div>
        <div class="stat"><div class="stat-num">{types}</div><div class="stat-label">Unique Types</div></div>
        <div class="stat"><div class="stat-num">{avg_score}</div><div class="stat-label">Avg Confidence</div></div>
    </div>
    """, unsafe_allow_html=True)

    if result["entities"]:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="result-label">Detected Entities</div>', unsafe_allow_html=True)
        chips = "".join(
            f'<span class="entity-chip"><span class="etype">{e["type"]}</span>'
            f'<span class="evalue">{e["value"]}</span>'
            f'<span class="escore">{e["score"]}</span></span>'
            for e in result["entities"]
        )
        st.markdown(f'<div style="margin-top:0.5rem">{chips}</div>', unsafe_allow_html=True)

elif run:
    st.warning("Please enter some text first.")