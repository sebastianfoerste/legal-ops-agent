"""
Agent J: The Interview Processor
Purpose: Automate the transformation of meeting transcripts into high-status emails and management memos.
Author: Google Antigravity (2026)
"""

from __future__ import annotations

import os
import time
from datetime import datetime

from dotenv import load_dotenv
from google import genai

try:
    from agents.prompt_guardrails import (
        PromptBudget,
        SummaryPayload,
        TranscriptChunk,
        build_hierarchical_summary,
        reduce_summary_payloads,
        render_summary_payloads,
    )
except ImportError:  # pragma: no cover - supports direct script execution.
    from prompt_guardrails import (  # type: ignore
        PromptBudget,
        SummaryPayload,
        TranscriptChunk,
        build_hierarchical_summary,
        reduce_summary_payloads,
        render_summary_payloads,
    )

# Load credentials
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

TRANSCRIPT_CHUNK_SUMMARY_PROMPT = """
TASK: TRANSCRIPT CHUNK SUMMARY
TRANSCRIPT CHUNK {chunk_index}/{total_chunks}

You are the structured note-taker for Sebastian, a partner at gunnercooke.
Extract only what is explicitly stated in this interview excerpt.
Do not invent facts.

Language: {language_full}
Candidate Name: {candidate_name}

Return concise bullet points under exactly these headings:
- Hard Skills & Expertise
- Business Case
- Motivation
- Decisions / Next Steps
- Risks / Open Questions
- Notable Quotes / Numbers

If a category is not supported by the excerpt, write "not stated".

Transcript excerpt:
{transcript_chunk}
"""

SUMMARY_REDUCTION_PROMPT = """
TASK: SUMMARY REDUCTION PASS
SUMMARY REDUCTION PASS {reduction_index}

You are consolidating interview notes into one compact evidence brief.
Merge the summaries below without losing concrete facts, names, or numbers.
Do not invent or infer details.

Language: {language_full}
Candidate Name: {candidate_name}

Return concise bullet points under exactly these headings:
- Hard Skills & Expertise
- Business Case
- Motivation
- Decisions / Next Steps
- Risks / Open Questions
- Notable Quotes / Numbers

Summaries to merge:
{summary_group}
"""

WOLF_SCHNEIDER_EMAIL_PROMPT = """
TASK: FINAL EMAIL SYNTHESIS
You are the Executive Assistant and Protokollführer for Sebastian, a partner at gunnercooke.
Your work is characterized by legal precision and an excellent writing style.

### CORE PROTOCOLS (STRICTANTS):
1. NO DASHES: Never use the signs '–' or '—'. Use commas, colons, or parentheses instead.
2. NO ABBREVIATIONS: Write everything out (e.g., "zum Beispiel", "Rechtsanwaltsgesellschaft").
3. NO COMMA AFTER GREETING: After the closing (e.g., "Beste Grüße"), do NOT use a comma.
4. CAPITALIZATION: The first sentence after the salutation (e.g., "Hallo Wolfgang") must start with a capital letter.
5. NO EMOJIS.
6. STIL: Write in the style of Wolf Schneider. Use active verbs, avoid nominalizations (no "-ung", "-heit", "-keit", "-ität"). Use short, clear sentences. No filler words.
7. SOURCE DISCIPLINE: Use only the structured evidence brief below. If a detail is missing, leave it out.

### INPUT:
Structured Evidence Brief:
{evidence_brief}

Date of Meeting: {date}
Candidate Name: {candidate_name}
Language: {language}

### STRUCTURE:
1. Salutation: "Hallo {recipient}".
2. Introduction: "Ich habe am {date} mit {candidate_name} gesprochen."
3. Body: A factual summary of the candidate focusing on:
   - Hard Skills & Expertise.
   - Business Case (Portable revenue/clients).
   - Motivation for joining gunnercooke.
4. Call to Action: "Er/Sie möchte nun gerne mit Dir sprechen."
5. Contact Details:
   "Seine/Ihre E-Mail-Adresse lautet"

   {email_address}

6. Closing:
   Beste Grüße

   Sebastian

Output only the email content.
"""

MANAGEMENT_MEMO_PROMPT = """
TASK: FINAL MANAGEMENT MEMO
Based on the following structured evidence brief, create a structured Management Analysis.
Use only the facts in the evidence brief.
Bold the categories.

Categories:
1. **Metadaten**: Datum, Meeting-Typ (Partner-Interview), Teilnehmer (Sebastian & {candidate_name}).
2. **Management Summary**: 100-150 words. Focus: Is the candidate "Partner-Material"?
3. **Detaillierte Gesprächspunkte**:
   - Werdegang & Expertise
   - Business Case (Specific numbers/names if mentioned)
   - Motivation
4. **Entscheidungen**: What was agreed upon?
5. **Nächste Schritte**: A markdown table with [Aufgabe] | [Verantwortlich] | [Frist].
6. **Risiken/Offene Fragen**.

Language: {language_full}

Structured Evidence Brief:
{evidence_brief}
"""


class InterviewProcessorError(RuntimeError):
    """Raised when Agent J cannot safely complete the interview processing flow."""


class InterviewProcessor:
    def __init__(
        self,
        model_id: str = "gemini-3-flash-preview",
        prompt_budget: PromptBudget | None = None,
    ):
        self.model_id = model_id
        self.prompt_budget = prompt_budget or PromptBudget()
        self.retry_delay_seconds = 5
        if GOOGLE_API_KEY:
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
        else:
            self.client = None

    def detect_language(self, text: str) -> str:
        """Roughly detect if text is German or English."""
        if " und " in text or " der " in text or " die " in text:
            return "DE"
        return "EN"

    def _generate_with_fallback(self, prompt: str) -> str:
        """Try multiple models, but fail cleanly if they all fail."""
        if not self.client:
            raise InterviewProcessorError("GOOGLE_API_KEY not found in environment.")

        prompt_len = len(prompt)
        if prompt_len > self.prompt_budget.input_budget_chars:
            raise InterviewProcessorError(
                f"Prompt budget exceeded ({prompt_len}/{self.prompt_budget.input_budget_chars} chars)."
            )

        models = [self.model_id, "gemini-pro-latest", "gemini-flash-latest"]
        last_error: Exception | None = None
        for model_name in models:
            try:
                response = self.client.models.generate_content(model=model_name, contents=prompt)
                text = (response.text or "").strip()
                if not text:
                    raise InterviewProcessorError(f"Model {model_name} returned an empty response.")
                return text
            except Exception as exc:  # pragma: no cover - exercised via processor behavior.
                last_error = exc
                print(f"  ⚠️ Model {model_name} failed: {exc}")
                if self.retry_delay_seconds > 0:
                    time.sleep(self.retry_delay_seconds)

        raise InterviewProcessorError(
            "Unable to process interview after exhausting model fallbacks."
        ) from last_error

    def _summarize_chunk(
        self,
        chunk: TranscriptChunk,
        candidate_name: str,
        language_full: str,
    ) -> str:
        prompt = TRANSCRIPT_CHUNK_SUMMARY_PROMPT.format(
            chunk_index=chunk.index,
            total_chunks=chunk.total_chunks,
            language_full=language_full,
            candidate_name=candidate_name,
            transcript_chunk=chunk.text,
        )
        return self._generate_with_fallback(prompt)

    def _reduce_summary_group(
        self,
        payloads: list[SummaryPayload],
        candidate_name: str,
        language_full: str,
        reduction_index: int,
    ) -> str:
        prompt = SUMMARY_REDUCTION_PROMPT.format(
            reduction_index=reduction_index,
            language_full=language_full,
            candidate_name=candidate_name,
            summary_group=render_summary_payloads(payloads),
        )
        return self._generate_with_fallback(prompt)

    def _build_prompt_with_evidence(
        self,
        template: str,
        evidence_payloads: list[SummaryPayload],
        candidate_name: str,
        language_full: str,
        prompt_fields: dict[str, str],
    ) -> str:
        fields = dict(prompt_fields)
        fields["evidence_brief"] = ""
        prompt_without_brief = template.format(**fields)
        available_chars = (
            self.prompt_budget.input_budget_chars - len(prompt_without_brief) - 200
        )
        if available_chars <= 0:
            raise InterviewProcessorError("Prompt template leaves no room for evidence context.")

        reduced_payloads = reduce_summary_payloads(
            evidence_payloads,
            lambda group, idx: self._reduce_summary_group(
                group,
                candidate_name=candidate_name,
                language_full=language_full,
                reduction_index=idx,
            ),
            available_chars,
        )
        evidence_brief = render_summary_payloads(reduced_payloads)

        fields["evidence_brief"] = evidence_brief
        prompt = template.format(**fields)
        if len(prompt) > self.prompt_budget.input_budget_chars:
            raise InterviewProcessorError("Unable to fit evidence brief within the prompt budget.")
        return prompt

    def process_interview(
        self,
        transcript: str,
        date: str,
        candidate_name: str,
        email: str = "[EMAIL MISSING]",
    ) -> str:
        transcript_text = transcript.strip()
        if not transcript_text:
            return "Error: Transcript is empty."

        try:
            lang = self.detect_language(transcript_text)
            recipient = "Wolfgang" if lang == "DE" else "James"
            lang_full = "German" if lang == "DE" else "English"

            print(f"Processing interview for {candidate_name} ({lang_full})...")

            _, evidence_payloads, _ = build_hierarchical_summary(
                transcript=transcript_text,
                budgets=self.prompt_budget,
                summarize_chunk=lambda chunk: self._summarize_chunk(
                    chunk,
                    candidate_name=candidate_name,
                    language_full=lang_full,
                ),
                reducer=lambda group, idx: self._reduce_summary_group(
                    group,
                    candidate_name=candidate_name,
                    language_full=lang_full,
                    reduction_index=idx,
                ),
                target_chars=self.prompt_budget.reduction_batch_size_chars,
            )

            email_prompt = self._build_prompt_with_evidence(
                WOLF_SCHNEIDER_EMAIL_PROMPT,
                evidence_payloads=evidence_payloads,
                candidate_name=candidate_name,
                language_full=lang_full,
                prompt_fields={
                    "date": date,
                    "candidate_name": candidate_name,
                    "language": lang_full,
                    "recipient": recipient,
                    "email_address": email,
                },
            )
            email_draft = self._generate_with_fallback(email_prompt)

            memo_prompt = self._build_prompt_with_evidence(
                MANAGEMENT_MEMO_PROMPT,
                evidence_payloads=evidence_payloads,
                candidate_name=candidate_name,
                language_full=lang_full,
                prompt_fields={
                    "candidate_name": candidate_name,
                    "language_full": lang_full,
                },
            )
            memo_text = self._generate_with_fallback(memo_prompt)

            output = f"""
# RECRUITING REPORT: {candidate_name}
Date: {date}

---

## PART 1: EMAIL DRAFT ({recipient})

{email_draft}

---

## PART 2: MANAGEMENT ANALYSIS

{memo_text}

---

## PART 3: VERBATIM TRANSCRIPT (EXCERPT)
{transcript_text[:2000]}... [Full transcript attached in source]
"""
            return output
        except InterviewProcessorError as exc:
            return f"Error: {exc}"


if __name__ == "__main__":
    sample_transcript = """
    Sebastian: Hallo, danke dass Sie sich Zeit nehmen. Erzählen Sie mal von Ihrem Business Case.
    Kandidat: Ich bringe ein Team von 3 Leuten mit und ca. 600k Umsatz aus dem Bereich M&A.
    Ich möchte weg von der aktuellen Kanzlei, weil die Strukturen zu starr sind.
    Gunnercooke scheint mir da flexibler zu sein.
    """

    agent = InterviewProcessor()
    result = agent.process_interview(
        transcript=sample_transcript,
        date=datetime.now().strftime("%Y-%m-%d"),
        candidate_name="Dr. Testkandidat",
        email="test@example.com",
    )

    output_path = os.path.join(os.path.dirname(__file__), "../output_test_interview.md")
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(result)

    print(f"Processing complete. Sample output saved to {output_path}.")
