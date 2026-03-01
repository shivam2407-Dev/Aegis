import re
from gliner import GLiNER
from transformers import pipeline as hf_pipeline

gliner     = GLiNER.from_pretrained("knowledgator/gliner-pii-small-v1.0")
classifier = hf_pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

PII_LABELS = [
    "person name",
    "email address",
    "phone number",
    "password or secret value",
    "api key or token",
    "id number or reference number",
    "credit card number",
    "social security number",
    "date of birth",
    "ip address",
    "username",
    "passport number",
    "bank account number",
]

LOC_LABELS = ["location", "country", "city", "region"]

THRESHOLD = 0.4

_INFORMAL_SECRET_RE = re.compile(
    r'(?i)\b(pass|password|passwd|secret|token|key)\s+([A-Za-z0-9@#$!%^&*]{4,})'
)
_EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')


def _is_personal_location(text: str, location: str) -> bool:
    result = classifier(
        f'In the sentence "{text}", the place "{location}" is',
        candidate_labels=["where the speaker personally lives, is from, or was born",
                          "a travel destination, business location, or general reference"],
    )
    return result["labels"][0] == "where the speaker personally lives, is from, or was born"


def _extract_sensitive_locations(text: str) -> list:
    loc_entities = gliner.predict_entities(text, LOC_LABELS, threshold=THRESHOLD)
    entities     = []
    for e in loc_entities:
        if _is_personal_location(text, e["text"]):
            entities.append({**e, "label": "personal location"})
    return entities


def _fallback_entities(text: str) -> list:
    entities = []
    for m in _EMAIL_RE.finditer(text):
        entities.append({"label": "email address", "text": m.group(), "start": m.start(), "end": m.end(), "score": 1.0})
    for m in _INFORMAL_SECRET_RE.finditer(text):
        entities.append({"label": "password or secret value", "text": m.group(2), "start": m.start(2), "end": m.end(2), "score": 1.0})
    return entities


def _resolve_overlaps(entities: list) -> list:
    resolved, last_end = [], -1
    for e in sorted(entities, key=lambda x: (x["start"], -x["score"])):
        if e["start"] >= last_end:
            resolved.append(e)
            last_end = e["end"]
    return resolved


def _apply_redaction(text: str, entities: list) -> str:
    result, cursor = "", 0
    for e in sorted(entities, key=lambda x: x["start"]):
        result += text[cursor:e["start"]] + f"<{e['label'].upper().replace(' ', '_')}>"
        cursor  = e["end"]
    return result + text[cursor:]


def redact_text(text: str) -> dict:
    pii_entities = gliner.predict_entities(text, PII_LABELS, threshold=THRESHOLD)
    all_entities = _resolve_overlaps(
        pii_entities                    +
        _extract_sensitive_locations(text) +
        _fallback_entities(text)
    )
    return {
        "original": text,
        "redacted": _apply_redaction(text, all_entities),
        "entities": [{"type": e["label"], "value": e["text"], "score": round(e["score"], 2)} for e in all_entities],
    }


def redact_dataframe(df, col: str):
    df = df.copy()
    df["redacted"] = df[col].apply(lambda x: redact_text(str(x))["redacted"])
    return df

str = input("Enter the Prompt : ")
print(redact_text(str))