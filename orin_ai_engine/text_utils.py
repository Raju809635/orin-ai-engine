from __future__ import annotations

import re
from typing import Iterable


NOISE_PATTERNS = [
    r"^\s*page\s+\d+\s*$",
    r"^\s*\d+\s*$",
    r"^\s*(unit|chapter)\s*$",
    r"^[xmtfepd\s\d:;./\\-]{20,}$",
    r".*(xxx|mmm|fff|pppmmm|aaammm|\.pdf|government.?s gift|textbook development).*",
    r".*\b(retpahc|nany|coammon|originationg|fornt)\b.*",
]


def repair_mojibake(value: str) -> str:
    if "à" not in value and "Ã" not in value:
        return value
    try:
        repaired = value.encode("latin1").decode("utf-8")
    except UnicodeError:
        return value
    original_indic = len(re.findall(r"[\u0900-\u097F\u0C00-\u0C7F]", value))
    repaired_indic = len(re.findall(r"[\u0900-\u097F\u0C00-\u0C7F]", repaired))
    return repaired if repaired_indic > original_indic else value


def clean_text(value: object) -> str:
    text = repair_mojibake(str(value or "")).replace("\u0000", " ")
    text = re.sub(r"[\uf0b4\u00d7]", " x ", text)
    text = re.sub(r"\bX{2,}\s+M{2,}.*?(?:A|P)M\b", " ", text, flags=re.I)
    text = re.sub(r"\b(?:math|maths|mathematics|telugu|english|hindi|physics|biology|social)\s+.*?\.pdf\b", " ", text, flags=re.I)
    text = re.sub(r"\b(?:final|inner|website|qr codes)\b", " ", text, flags=re.I)
    text = re.sub(r"\b\d{1,4}[/:-]\d{1,4}[/:-]\d{1,4}\b", " ", text)
    text = re.sub(r"\b\d{1,3}[:]\d{1,3}[:]\d{1,3}\b", " ", text)
    text = re.sub(r"\b[\d/:]{12,}\b", " ", text)
    text = re.sub(r"\b\d{4,}\b", " ", text)
    text = re.sub(r"\b(?:PPPMMM|AAAMMM|RETPAHC|Nany|CoAmmon|originationg|fornt)\b", " ", text, flags=re.I)
    text = re.sub(r"(?<=[a-z])[A-Z](?=[a-z])", "", text)
    text = re.sub(r"\b[A-Z]\b", " ", text)
    text = re.sub(r"([A-Za-z])\1{3,}", r"\1", text)
    text = re.sub(r"\b(?:pdf|final|em)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b\d{2,}[-/:]\d{2,}[-/:]\d{2,}\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_for_subject(value: object, subject: str = "") -> str:
    text = clean_text(value)
    if subject.lower() in {"telugu", "hindi"}:
        text = re.sub(r"\b[A-Za-z]{2,}\b", " ", text)
        text = re.sub(r"\b[A-Za-z]\b", " ", text)
        text = re.sub(r"[<>|_=~^`{}\\]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
    return text


def is_useful_text(value: object, min_chars: int = 24) -> bool:
    text = clean_text(value)
    if len(text) < min_chars:
        return False
    lower = text.lower()
    if any(re.match(pattern, lower) for pattern in NOISE_PATTERNS):
        return False
    letters = re.findall(r"[A-Za-z\u0900-\u097F\u0C00-\u0C7F0-9]", text)
    if len(letters) < min_chars // 2:
        return False
    weird = len(re.findall(r"[~_=|{}<>\\^`]", text))
    if weird >= 2:
        return False
    return True


def unique_strings(values: Iterable[object], limit: int = 100) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = clean_text(value)
        key = text.lower()
        if not text or key in seen:
            continue
        seen.add(key)
        output.append(text)
        if len(output) >= limit:
            break
    return output


def split_sentences(text: str) -> list[str]:
    clean = clean_text(text)
    if not clean:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", clean) if part.strip()]


def semantic_windows(text: str, max_chars: int = 850, overlap_sentences: int = 1) -> list[str]:
    sentences = [sentence for sentence in split_sentences(text) if is_useful_text(sentence, min_chars=18)]
    if not sentences:
        return [clean_text(text)] if is_useful_text(text) else []

    windows: list[str] = []
    index = 0
    while index < len(sentences):
        current: list[str] = []
        length = 0
        start = index
        while index < len(sentences):
            sentence = sentences[index]
            if current and length + len(sentence) > max_chars:
                break
            current.append(sentence)
            length += len(sentence) + 1
            index += 1
        if current:
            windows.append(clean_text(" ".join(current)))
        if index >= len(sentences):
            break
        index = max(start + 1, index - overlap_sentences)
    return unique_strings(windows, limit=1000)
