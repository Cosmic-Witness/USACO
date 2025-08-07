from typing import Optional
from datetime import date
import os

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class HomeworkGenerator:
    def __init__(self, openai_api_key: Optional[str], model: str) -> None:
        self.openai_api_key = openai_api_key
        self.model = model
        self._client = None
        if self.openai_api_key and OpenAI is not None:
            self._client = OpenAI(api_key=self.openai_api_key)

    def generate(
        self,
        subject: str,
        topic: str,
        level: str,
        num_questions: int,
        due_date: str,
        teacher_name: Optional[str] = None,
    ) -> str:
        if self._client is None:
            return self._fallback(subject, topic, level, num_questions, due_date, teacher_name)

        system_prompt = (
            "You are a helpful assistant that writes clear, age-appropriate homework. "
            "Return only markdown with headings and numbered questions. Include an answer key at the end."
        )
        user_prompt = (
            f"Create homework for subject: {subject}.\n"
            f"Topic: {topic}.\n"
            f"Level: {level}.\n"
            f"Number of questions: {num_questions}.\n"
            f"Due date: {due_date}.\n"
            f"Teacher: {teacher_name or 'Unknown'}.\n\n"
            "Structure: \n"
            "# Title with subject and topic\n"
            "## Instructions\n"
            "## Questions (numbered 1..N)\n"
            "## Answer Key\n"
        )

        try:
            # Prefer Responses API when available
            if hasattr(self._client, "responses"):
                resp = self._client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                # Extract text from responses
                text_chunks = []
                for out in resp.output or []:  # type: ignore[attr-defined]
                    if getattr(out, "type", "") == "output_text":
                        text_chunks.append(getattr(out, "content", ""))
                content = "\n".join(text_chunks).strip()
            else:
                # Fallback to chat.completions
                chat = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                )
                content = chat.choices[0].message.content or ""
        except Exception:
            content = self._fallback(subject, topic, level, num_questions, due_date, teacher_name)

        return content.strip()

    def _fallback(
        self,
        subject: str,
        topic: str,
        level: str,
        num_questions: int,
        due_date: str,
        teacher_name: Optional[str],
    ) -> str:
        lines = []
        lines.append(f"# {subject} Homework: {topic}")
        lines.append("")
        lines.append(f"Level: {level}  ")
        lines.append(f"Due: {due_date}  ")
        if teacher_name:
            lines.append(f"Teacher: {teacher_name}")
        lines.append("")
        lines.append("## Instructions")
        lines.append("Show all your work and submit by the due date.")
        lines.append("")
        lines.append("## Questions")
        for i in range(1, num_questions + 1):
            lines.append(f"{i}. Describe or solve a problem related to {topic} at the {level} level.")
        lines.append("")
        lines.append("## Answer Key")
        for i in range(1, num_questions + 1):
            lines.append(f"{i}. Answers will be provided by the teacher after submission.")
        return "\n".join(lines)