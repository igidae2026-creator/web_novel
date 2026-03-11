from __future__ import annotations

import re
from collections import Counter
from statistics import mean
from typing import Any, Dict, List


_SENTENCE_SPLIT_RE = re.compile(r"(?:[.!?…]+|[\r\n]+)")
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")


def _normalize(fragment: str) -> str:
    return "".join(str(fragment or "").split())


def _split_sentences(text: str) -> List[str]:
    chunks = [_normalize(part) for part in _SENTENCE_SPLIT_RE.split(str(text or ""))]
    return [chunk for chunk in chunks if chunk]


def _split_paragraphs(text: str) -> List[str]:
    chunks = [_normalize(part) for part in _PARAGRAPH_SPLIT_RE.split(str(text or ""))]
    return [chunk for chunk in chunks if chunk]


def evaluate_prose_readability(text: str) -> Dict[str, Any]:
    sentences = _split_sentences(text)
    paragraphs = _split_paragraphs(text)
    paragraph_sentence_counts = [
        len(_split_sentences(paragraph))
        for paragraph in _PARAGRAPH_SPLIT_RE.split(str(text or ""))
        if _normalize(paragraph)
    ]

    if not sentences:
        return {
            "score": 0.0,
            "issues": ["empty_or_unreadable_text"],
            "sentence_count": 0,
            "average_sentence_length": 0.0,
            "max_sentence_length": 0,
            "max_paragraph_length": 0,
            "long_sentence_ratio": 1.0,
            "dense_paragraph_ratio": 1.0,
            "crowded_paragraph_ratio": 1.0,
            "repetitive_opening_ratio": 1.0,
        }

    sentence_lengths = [len(sentence) for sentence in sentences]
    paragraph_lengths = [len(paragraph) for paragraph in paragraphs] or [len(_normalize(text))]
    openings = [sentence[:8] for sentence in sentences if len(sentence) >= 8]
    opening_counts = Counter(openings)
    repeated_openings = sum(count - 1 for count in opening_counts.values() if count > 1)

    average_sentence_length = float(mean(sentence_lengths))
    max_sentence_length = max(sentence_lengths)
    max_paragraph_length = max(paragraph_lengths)
    long_sentence_ratio = sum(length >= 72 for length in sentence_lengths) / len(sentence_lengths)
    very_long_sentence_ratio = sum(length >= 110 for length in sentence_lengths) / len(sentence_lengths)
    dense_paragraph_ratio = sum(length >= 220 for length in paragraph_lengths) / len(paragraph_lengths)
    crowded_paragraph_ratio = (
        sum(count >= 4 for count in paragraph_sentence_counts) / len(paragraph_sentence_counts)
        if paragraph_sentence_counts
        else 1.0
    )
    repetitive_opening_ratio = repeated_openings / len(sentence_lengths)

    score = 0.92
    score -= min(0.24, max(0.0, average_sentence_length - 40.0) / 45.0 * 0.24)
    score -= min(0.18, long_sentence_ratio * 0.24)
    score -= min(0.16, very_long_sentence_ratio * 0.28)
    score -= min(0.18, dense_paragraph_ratio * 0.22)
    score -= min(0.24, crowded_paragraph_ratio * 0.26)
    score -= min(0.14, repetitive_opening_ratio * 0.32)
    if max_paragraph_length >= 360:
        score -= 0.08
    if max(paragraph_sentence_counts or [0]) >= 5:
        score -= 0.08
    if len(sentences) < 4:
        score -= 0.05
    score = max(0.0, min(1.0, score))

    issues: List[str] = []
    if average_sentence_length > 46:
        issues.append("dense_sentence_flow")
    if long_sentence_ratio > 0.34 or max_sentence_length >= 110:
        issues.append("overlong_sentences")
    if dense_paragraph_ratio > 0.34 or max_paragraph_length >= 260:
        issues.append("wall_of_text")
    if crowded_paragraph_ratio > 0.34 or max(paragraph_sentence_counts or [0]) >= 5:
        issues.append("crowded_paragraphs")
    if repetitive_opening_ratio > 0.25:
        issues.append("repetitive_sentence_openings")

    return {
        "score": round(score, 4),
        "issues": issues,
        "sentence_count": len(sentence_lengths),
        "average_sentence_length": round(average_sentence_length, 2),
        "max_sentence_length": max_sentence_length,
        "max_paragraph_length": max_paragraph_length,
        "long_sentence_ratio": round(long_sentence_ratio, 4),
        "dense_paragraph_ratio": round(dense_paragraph_ratio, 4),
        "crowded_paragraph_ratio": round(crowded_paragraph_ratio, 4),
        "repetitive_opening_ratio": round(repetitive_opening_ratio, 4),
    }
