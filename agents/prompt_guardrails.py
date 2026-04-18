from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Callable

SPEAKER_PATTERN = re.compile(r"^\s*[A-Za-zÄÖÜäöüß][^:\n]{0,80}:\s*")


@dataclass(frozen=True)
class PromptBudget:
    input_budget_chars: int = 8_000
    raw_chunk_size_chars: int = 3_000
    reduction_batch_size_chars: int = 6_000


@dataclass(frozen=True)
class TranscriptChunk:
    index: int
    total_chunks: int
    text: str
    char_count: int


@dataclass(frozen=True)
class SummaryPayload:
    index: int
    text: str
    char_count: int
    level: int = 0
    source_indices: tuple[int, ...] = field(default_factory=tuple)


ChunkSummarizer = Callable[[TranscriptChunk], str]
SummaryReducer = Callable[[list[SummaryPayload], int], str]


def split_transcript_blocks(transcript: str) -> list[str]:
    normalized = transcript.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []

    blocks: list[str] = []
    current: list[str] = []
    for line in normalized.split("\n"):
        stripped = line.strip()
        if not stripped:
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            continue

        if SPEAKER_PATTERN.match(stripped) and current:
            blocks.append("\n".join(current).strip())
            current = [stripped]
            continue

        current.append(stripped)

    if current:
        blocks.append("\n".join(current).strip())

    return [block for block in blocks if block]


def hard_wrap_text(text: str, max_chars: int) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]

    wrapped: list[str] = []
    remaining = cleaned
    while len(remaining) > max_chars:
        candidate = remaining[: max_chars + 1]
        split_at = max(
            candidate.rfind("\n"),
            candidate.rfind(". "),
            candidate.rfind("? "),
            candidate.rfind("! "),
            candidate.rfind("; "),
            candidate.rfind(", "),
            candidate.rfind(" "),
        )
        if split_at < max_chars // 2:
            split_at = max_chars

        piece = remaining[:split_at].strip()
        if not piece:
            piece = remaining[:max_chars].strip()
            split_at = max_chars
        wrapped.append(piece)
        remaining = remaining[split_at:].lstrip()

    if remaining:
        wrapped.append(remaining.strip())

    return [piece for piece in wrapped if piece]


def chunk_transcript(transcript: str, max_chars: int) -> list[TranscriptChunk]:
    raw_blocks = split_transcript_blocks(transcript)
    if not raw_blocks:
        return []

    blocks: list[str] = []
    for block in raw_blocks:
        if len(block) <= max_chars:
            blocks.append(block)
            continue
        blocks.extend(hard_wrap_text(block, max_chars))

    chunk_texts: list[str] = []
    current_blocks: list[str] = []
    current_len = 0

    for block in blocks:
        separator_len = 2 if current_blocks else 0
        if current_blocks and current_len + separator_len + len(block) > max_chars:
            chunk_texts.append("\n\n".join(current_blocks).strip())
            current_blocks = [block]
            current_len = len(block)
            continue

        current_blocks.append(block)
        current_len += separator_len + len(block)

    if current_blocks:
        chunk_texts.append("\n\n".join(current_blocks).strip())

    total_chunks = len(chunk_texts)
    return [
        TranscriptChunk(
            index=index,
            total_chunks=total_chunks,
            text=text,
            char_count=len(text),
        )
        for index, text in enumerate(chunk_texts, start=1)
    ]


def summarize_chunks(chunks: list[TranscriptChunk], summarizer: ChunkSummarizer) -> list[SummaryPayload]:
    payloads: list[SummaryPayload] = []
    for chunk in chunks:
        summary_text = summarizer(chunk).strip()
        payloads.append(
            SummaryPayload(
                index=chunk.index,
                text=summary_text,
                char_count=len(summary_text),
                level=0,
                source_indices=(chunk.index,),
            )
        )
    return payloads


def render_summary_payloads(payloads: list[SummaryPayload]) -> str:
    rendered: list[str] = []
    for payload in payloads:
        sources = ", ".join(str(source) for source in payload.source_indices) or str(payload.index)
        rendered.append(
            f"[Summary {payload.index} | level {payload.level} | source chunks: {sources}]\n"
            f"{payload.text.strip()}"
        )
    return "\n\n".join(rendered).strip()


def normalize_payload_sizes(payloads: list[SummaryPayload], max_chars: int) -> list[SummaryPayload]:
    normalized: list[SummaryPayload] = []
    next_index = 1
    for payload in payloads:
        if payload.char_count <= max_chars:
            normalized.append(
                SummaryPayload(
                    index=next_index,
                    text=payload.text,
                    char_count=payload.char_count,
                    level=payload.level,
                    source_indices=payload.source_indices,
                )
            )
            next_index += 1
            continue

        for piece in hard_wrap_text(payload.text, max_chars):
            normalized.append(
                SummaryPayload(
                    index=next_index,
                    text=piece,
                    char_count=len(piece),
                    level=payload.level,
                    source_indices=payload.source_indices,
                )
            )
            next_index += 1
    return normalized


def group_summary_payloads(payloads: list[SummaryPayload], max_chars: int) -> list[list[SummaryPayload]]:
    normalized = normalize_payload_sizes(payloads, max_chars)
    groups: list[list[SummaryPayload]] = []
    current_group: list[SummaryPayload] = []
    current_len = 0

    for payload in normalized:
        payload_len = len(render_summary_payloads([payload]))
        separator_len = 2 if current_group else 0
        if current_group and current_len + separator_len + payload_len > max_chars:
            groups.append(current_group)
            current_group = [payload]
            current_len = payload_len
            continue

        current_group.append(payload)
        current_len += separator_len + payload_len

    if current_group:
        groups.append(current_group)

    return groups


def reduce_summary_payloads(
    payloads: list[SummaryPayload],
    reducer: SummaryReducer,
    max_chars: int,
) -> list[SummaryPayload]:
    current = payloads[:]
    while True:
        rendered = render_summary_payloads(current)
        if rendered and len(rendered) <= max_chars:
            return current

        groups = group_summary_payloads(current, max_chars)
        if len(groups) == 1 and len(current) == 1:
            return current

        reduced_payloads: list[SummaryPayload] = []
        for group_index, group in enumerate(groups, start=1):
            reduced_text = reducer(group, group_index).strip()
            source_indices = tuple(
                sorted({source for payload in group for source in payload.source_indices})
            )
            reduced_payloads.append(
                SummaryPayload(
                    index=group_index,
                    text=reduced_text,
                    char_count=len(reduced_text),
                    level=max((payload.level for payload in group), default=0) + 1,
                    source_indices=source_indices,
                )
            )
        current = reduced_payloads


def build_hierarchical_summary(
    transcript: str,
    budgets: PromptBudget,
    summarize_chunk: ChunkSummarizer,
    reducer: SummaryReducer,
    target_chars: int | None = None,
) -> tuple[list[TranscriptChunk], list[SummaryPayload], str]:
    chunks = chunk_transcript(transcript, budgets.raw_chunk_size_chars)
    payloads = summarize_chunks(chunks, summarize_chunk)
    max_chars = target_chars or budgets.reduction_batch_size_chars
    reduced_payloads = reduce_summary_payloads(payloads, reducer, max_chars)
    return chunks, reduced_payloads, render_summary_payloads(reduced_payloads)
