"""Prompt-driven DOCX editing helpers.

This module turns a user prompt into either:
1. Surgical DOCX instructions, applied with the existing DocxEditor helper.
2. A best-effort rewritten document when the prompt is more open-ended.

The implementation is intentionally layered:
- deterministic parsing for common edit requests
- optional LLM planning if GROQ_API_KEY or OPENAI_API_KEY is available
- fallback behavior that still works without any external API
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import io
import shutil
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from utils.docx_editor import DocxCreator, DocxEditor, ai_edit_document


@dataclass
class PromptEditResult:
    """Result payload returned by prompt-driven edits."""

    output_path: str
    summary: str
    strategy: str
    instructions: List[Dict[str, Any]]


def extract_docx_text(source: Any) -> str:
    """Extract text from a DOCX path, bytes, or file-like object."""
    if isinstance(source, (bytes, bytearray)):
        return extract_docx_text_from_bytes(bytes(source))

    doc = Document(source)
    parts: List[str] = []

    for index, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text:
            parts.append(f"[P{index}] {text}")

    for table_index, table in enumerate(doc.tables):
        parts.append(f"[TABLE {table_index}]")
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            if row_text.strip():
                parts.append(row_text)

    for section_index, section in enumerate(doc.sections):
        header_text = " ".join(p.text.strip() for p in section.header.paragraphs if p.text.strip())
        footer_text = " ".join(p.text.strip() for p in section.footer.paragraphs if p.text.strip())
        if header_text:
            parts.append(f"[HEADER {section_index}] {header_text}")
        if footer_text:
            parts.append(f"[FOOTER {section_index}] {footer_text}")

    return "\n".join(parts)


def extract_docx_text_from_bytes(data: bytes) -> str:
    """Extract text from DOCX bytes."""
    doc = Document(io.BytesIO(data))
    parts: List[str] = []

    for index, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text:
            parts.append(f"[P{index}] {text}")

    for table_index, table in enumerate(doc.tables):
        parts.append(f"[TABLE {table_index}]")
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            if row_text.strip():
                parts.append(row_text)

    for section_index, section in enumerate(doc.sections):
        header_text = " ".join(p.text.strip() for p in section.header.paragraphs if p.text.strip())
        footer_text = " ".join(p.text.strip() for p in section.footer.paragraphs if p.text.strip())
        if header_text:
            parts.append(f"[HEADER {section_index}] {header_text}")
        if footer_text:
            parts.append(f"[FOOTER {section_index}] {footer_text}")

    return "\n".join(parts)


def _inline_markdown_to_runs(paragraph, text: str) -> None:
    """Render simple inline markdown like **bold** and *italic*."""
    tokens = re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith("*") and token.endswith("*"):
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        else:
            paragraph.add_run(token)


def markdown_to_docx_bytes(markdown: str, title: str = "Edited Document") -> bytes:
    """Convert a markdown-like draft into a DOCX file."""
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    if title:
        heading = doc.add_heading(title, level=0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    lines = [line.rstrip() for line in markdown.splitlines()]
    table_buffer: List[str] = []

    def flush_table() -> None:
        nonlocal table_buffer
        if len(table_buffer) < 2:
            table_buffer = []
            return

        header_cells = [cell.strip() for cell in table_buffer[0].strip("|").split("|")]
        body_rows: List[List[str]] = []
        for row in table_buffer[2:]:
            if row.strip() and "|" in row:
                body_rows.append([cell.strip() for cell in row.strip("|").split("|")])

        if not header_cells:
            table_buffer = []
            return

        table = doc.add_table(rows=1, cols=len(header_cells))
        table.style = "Table Grid"
        header = table.rows[0].cells
        for i, cell_text in enumerate(header_cells):
            header[i].text = cell_text
            if header[i].paragraphs and header[i].paragraphs[0].runs:
                header[i].paragraphs[0].runs[0].bold = True

        for row in body_rows:
            cells = table.add_row().cells
            for i in range(len(header_cells)):
                cells[i].text = row[i] if i < len(row) else ""
        table_buffer = []

    for raw_line in lines:
        line = raw_line.strip()

        if table_buffer:
            if line.startswith("|") and "|" in line:
                table_buffer.append(line)
                continue
            flush_table()

        if not line:
            doc.add_paragraph()
            continue

        if line.startswith("|") and "|" in line:
            table_buffer = [line]
            continue

        if line.startswith("### "):
            doc.add_heading(line[4:], level=3)
            continue
        if line.startswith("## "):
            doc.add_heading(line[3:], level=2)
            continue
        if line.startswith("# "):
            heading = doc.add_heading(line[2:], level=1)
            heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue

        if line.startswith(("- ", "* ")):
            doc.add_paragraph(line[2:], style="List Bullet")
            continue

        if re.match(r"^\d+[.)]\s+", line):
            doc.add_paragraph(re.sub(r"^\d+[.)]\s+", "", line), style="List Number")
            continue

        paragraph = doc.add_paragraph()
        _inline_markdown_to_runs(paragraph, line)

    flush_table()

    output = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    output.close()
    doc.save(output.name)
    with open(output.name, "rb") as handle:
        data = handle.read()
    os.unlink(output.name)
    return data


def _looks_like_rewrite_prompt(prompt: str) -> bool:
    rewrite_words = [
        "rewrite",
        "revise",
        "polish",
        "shorten",
        "expand",
        "summarize",
        "summarise",
        "make it sound",
        "make this sound",
        "change the tone",
        "professional",
        "formal",
        "casual",
        "convert",
    ]
    lowered = prompt.lower()
    return any(word in lowered for word in rewrite_words)


def _parse_structured_instructions(prompt: str) -> List[Dict[str, Any]]:
    """Parse common edit patterns from a prompt into DocxEditor instructions."""
    instructions: List[Dict[str, Any]] = []

    replace_patterns = [
        r'(?i)\b(?:replace|change|swap)\s+"([^"]+)"\s+(?:with|to)\s+"([^"]+)"',
        r"(?i)\b(?:replace|change|swap)\s+'([^']+)'\s+(?:with|to)\s+'([^']+)'",
    ]
    for pattern in replace_patterns:
        for old, new in re.findall(pattern, prompt):
            instructions.append({"action": "replace", "old": old, "new": new})

    delete_patterns = [
        r'(?i)\b(?:delete|remove)\s+"([^"]+)"',
        r"(?i)\b(?:delete|remove)\s+'([^']+)'",
    ]
    for pattern in delete_patterns:
        for text in re.findall(pattern, prompt):
            instructions.append({"action": "delete", "text": text})

    heading_patterns = [
        r'(?i)\badd heading\s+"([^"]+)"(?:\s+level\s+([1-6]))?',
        r"(?i)\badd heading\s+'([^']+)'(?:\s+level\s+([1-6]))?",
    ]
    for pattern in heading_patterns:
        for heading_text, level in re.findall(pattern, prompt):
            instructions.append({"action": "add_heading", "text": heading_text, "level": int(level or 1)})

    para_patterns = [
        r'(?i)\badd paragraph\s+"([^"]+)"',
        r"(?i)\badd paragraph\s+'([^']+)'",
    ]
    for pattern in para_patterns:
        for text in re.findall(pattern, prompt):
            instructions.append({"action": "add_paragraph", "text": text})

    bullet_patterns = [
        r'(?i)\badd bullet\s+"([^"]+)"',
        r"(?i)\badd bullet\s+'([^']+)'",
    ]
    for pattern in bullet_patterns:
        for text in re.findall(pattern, prompt):
            instructions.append({"action": "add_bullet", "text": text})

    comment_patterns = [
        r'(?i)\bcomment on\s+"([^"]+)"\s*:\s*"([^"]+)"',
        r"(?i)\bcomment on\s+'([^']+)'\s*:\s*'([^']+)'",
    ]
    for pattern in comment_patterns:
        for on_text, comment in re.findall(pattern, prompt):
            instructions.append({"action": "comment", "on": on_text, "text": comment})

    format_patterns = [
        r'(?i)\bformat\s+"([^"]+)"\s+(bold|italic|underline)',
        r"(?i)\bformat\s+'([^']+)'\s+(bold|italic|underline)",
    ]
    for pattern in format_patterns:
        for find_text, style in re.findall(pattern, prompt):
            payload = {"action": "format", "find": find_text}
            payload[style.lower()] = True
            instructions.append(payload)

    return instructions


def _try_llm_plan(prompt: str, document_text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Try to get a JSON edit plan from an LLM, if credentials are present."""
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None, "No LLM credentials configured."

    system_message = (
        "You are a document editing planner. Convert the user's request into a JSON object.\n"
        "Return ONLY valid JSON with keys: strategy, summary, instructions, rewritten_markdown.\n"
        "strategy must be either 'surgical' or 'rewrite'.\n"
        "For surgical edits, instructions must be an array of DocxEditor instructions.\n"
        "For rewrite, provide rewritten_markdown as a complete rewritten document.\n"
        "Use the exact action names supported by DocxEditor: replace, replace_tracked, insert_tracked, "
        "delete_tracked, comment, format, add_paragraph, add_heading, add_bullet, add_table.\n"
        "If you do not need a rewrite, leave rewritten_markdown empty."
    )
    user_message = (
        "DOCUMENT TEXT:\n"
        f"{document_text}\n\n"
        "USER PROMPT:\n"
        f"{prompt}\n"
    )

    try:
        try:
            from groq import Groq  # type: ignore

            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv("GROQ_DOCX_MODEL", "llama-3.3-70b-versatile"),
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or ""
        except Exception:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_DOCX_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or ""

        plan = json.loads(content)
        if not isinstance(plan, dict):
            return None, "LLM returned non-object JSON."
        return plan, "LLM plan generated successfully."
    except Exception as exc:
        return None, f"LLM plan generation failed: {exc}"


def apply_prompt_edit(
    input_path: str,
    prompt: str,
    output_path: Optional[str] = None,
    author: str = "AI Assistant",
) -> PromptEditResult:
    """Edit a DOCX file using a natural-language prompt."""
    editor = DocxEditor(input_path, author=author)
    document_text = editor.read_text()
    instructions = _parse_structured_instructions(prompt)
    summary_parts: List[str] = []

    if instructions:
        for instruction in instructions:
            action = instruction["action"]
            if action == "replace":
                count = editor.replace_text(instruction["old"], instruction["new"], case_sensitive=False)
                summary_parts.append(f"Replaced {count} occurrence(s) of '{instruction['old']}'.")
            elif action == "replace_tracked":
                editor.replace_tracked(instruction["paragraph"], instruction["old"], instruction["new"])
                summary_parts.append(f"Tracked replacement in paragraph {instruction['paragraph']}.")
            elif action == "insert_tracked":
                editor.insert_tracked(instruction["paragraph"], instruction["after"], instruction["text"])
                summary_parts.append(f"Tracked insertion in paragraph {instruction['paragraph']}.")
            elif action == "delete_tracked":
                editor.delete_tracked(instruction["paragraph"], instruction["text"])
                summary_parts.append(f"Tracked deletion in paragraph {instruction['paragraph']}.")
            elif action == "delete":
                count = editor.replace_text(instruction["text"], "", case_sensitive=False)
                summary_parts.append(f"Deleted {count} occurrence(s) of '{instruction['text']}'.")
            elif action == "comment":
                editor.add_comment(instruction["text"], on_text=instruction["on"], paragraph_index=instruction.get("paragraph"))
                summary_parts.append(f"Comment added on '{instruction['on']}'.")
            elif action == "format":
                editor.format_text(
                    instruction["find"],
                    bold=instruction.get("bold", False),
                    italic=instruction.get("italic", False),
                    underline=instruction.get("underline", False),
                    color_hex=instruction.get("color"),
                    font_size_pt=instruction.get("size"),
                )
                summary_parts.append(f"Formatted '{instruction['find']}'.")
            elif action == "add_paragraph":
                editor.add_paragraph(instruction["text"])
                summary_parts.append("Added a paragraph.")
            elif action == "add_heading":
                editor.add_heading(instruction["text"], level=instruction.get("level", 1))
                summary_parts.append(f"Added heading '{instruction['text']}'.")
            elif action == "add_bullet":
                editor.add_bullet(instruction["text"])
                summary_parts.append(f"Added bullet '{instruction['text']}'.")
            elif action == "add_table":
                editor.add_table(instruction["headers"], instruction["rows"])
                summary_parts.append("Added a table.")
            else:
                summary_parts.append(f"Skipped unsupported action '{action}'.")

        target = output_path or _default_output_path(input_path)
        editor.save(target)
        return PromptEditResult(
            output_path=target,
            summary=" ".join(summary_parts) if summary_parts else "Applied structured edits.",
            strategy="surgical",
            instructions=instructions,
        )

    llm_plan, llm_message = _try_llm_plan(prompt, document_text)
    if llm_plan and llm_plan.get("strategy") == "rewrite" and llm_plan.get("rewritten_markdown"):
        markdown = llm_plan["rewritten_markdown"]
        bytes_out = markdown_to_docx_bytes(markdown, title=os.path.basename(input_path).replace(".docx", ""))
        target = output_path or _default_output_path(input_path)
        with open(target, "wb") as handle:
            handle.write(bytes_out)
        return PromptEditResult(
            output_path=target,
            summary=llm_plan.get("summary") or "Rewrote the document from the prompt.",
            strategy="rewrite",
            instructions=llm_plan.get("instructions") or [],
        )

    if llm_plan and isinstance(llm_plan.get("instructions"), list) and llm_plan["instructions"]:
        target = output_path or _default_output_path(input_path)
        saved_path = ai_edit_document(input_path, llm_plan["instructions"], output_path=target, author=author)
        return PromptEditResult(
            output_path=saved_path,
            summary=llm_plan.get("summary") or "Applied LLM-generated surgical edits.",
            strategy=llm_plan.get("strategy", "surgical"),
            instructions=llm_plan["instructions"],
        )

    # Final fallback: if the prompt is more open-ended, do not fail.
    # Return a safe copy of the document so the UI can keep moving and tell
    # the user it needs a clearer edit instruction.
    if _looks_like_rewrite_prompt(prompt):
        draft = Document(input_path)
        draft.add_page_break()
        draft.add_heading("Revision Note", level=1)
        draft.add_paragraph(f"Prompt: {prompt}")
        draft.add_paragraph("No LLM credentials were configured, so the editor added a revision note instead of rewriting the full document.")
        target = output_path or _default_output_path(input_path)
        draft.save(target)
        return PromptEditResult(
            output_path=target,
            summary="Added a revision note because no LLM was available for a full rewrite.",
            strategy="fallback",
            instructions=[],
        )

    target = output_path or _default_output_path(input_path)
    shutil.copy2(input_path, target)
    return PromptEditResult(
        output_path=target,
        summary=(
            "I could not infer exact edits from that prompt, so I returned an unchanged copy. "
            "Try quoted edits like replace \"old\" with \"new\", add heading \"Summary\", or delete \"text\"."
        ),
        strategy="clarification",
        instructions=[],
    )


def edit_docx_bytes(
    file_bytes: bytes,
    prompt: str,
    output_path: Optional[str] = None,
    author: str = "AI Assistant",
) -> Tuple[bytes, PromptEditResult]:
    """Edit DOCX bytes and return the edited bytes plus a structured result."""
    output_is_temporary = output_path is None
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as input_handle:
        input_handle.write(file_bytes)
        input_handle.flush()
        input_path = input_handle.name

    try:
        if output_path:
            temp_output = output_path
        else:
            fd, temp_output = tempfile.mkstemp(suffix=".docx")
            os.close(fd)
        result = apply_prompt_edit(input_path=input_path, prompt=prompt, output_path=temp_output, author=author)
        with open(result.output_path, "rb") as handle:
            edited_bytes = handle.read()
        if output_is_temporary and os.path.exists(result.output_path):
            os.unlink(result.output_path)
        return edited_bytes, result
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)


def _default_output_path(input_path: str) -> str:
    base, ext = os.path.splitext(input_path)
    return base + "_edited" + ext
