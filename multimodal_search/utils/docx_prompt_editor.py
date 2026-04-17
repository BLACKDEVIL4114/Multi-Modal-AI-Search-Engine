import io
import re
import os
import zipfile
import tempfile
import shutil
from datetime import datetime
from docx import Document
from dataclasses import dataclass

@dataclass
class EditResult:
    strategy: str
    summary: str

def edit_docx_bytes(docx_bytes, prompt, author="AI Assistant"):
    """
    Surgical Docx Editing Engine for API usage.
    """
    # 1. Parse prompt for replacements (Simple "A" -> "B" or "A" to "B" logic)
    # In a real scenario, this would call LLM, but here we provide a robust parser.
    replacements = {}
    
    # Matches "old" -> "new" or "old" to "new"
    pairs = re.findall(r'["\'](.*?)["\']\s*(?:->|to)\s*["\'](.*?)["\']', prompt)
    if not pairs:
        # Fallback for plain text without quotes
        pairs = re.findall(r'(\w+)\s*(?:->|to)\s*(\w+)', prompt)
    
    for old, new in pairs:
        replacements[old.strip()] = new.strip()
    
    if not replacements:
        # If no specific pattern found, we might treat the whole prompt as a replacement if it has "X -> Y"
        match = re.search(r'(.*?)\s*(?:->|to)\s*(.*)', prompt)
        if match:
            replacements[match.group(1).strip()] = match.group(2).strip()

    if not replacements:
        return docx_bytes, EditResult(strategy="None", summary="No specific replacements detected in prompt.")

    try:
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
            
        xml_targets = []
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file.endswith(".xml"):
                    xml_targets.append(os.path.join(root, file))
                    
        total_swaps = 0
        date_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        for xml_path in xml_targets:
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            found_in_file = False
            for old, new in replacements.items():
                old_xml = old.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                new_xml = new.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                if old_xml in xml_content:
                    # Redline Surgery
                    def q_anchor(t):
                        words = t.split()
                        if not words: return re.escape(t)
                        return r'(?:<[^>]+>|\s)*'.join([re.escape(w) for w in words])

                    pattern = q_anchor(old_xml)
                    match = re.search(f'(<w:rPr>.*?</w:rPr>)?(?:<[^>]+>)*({pattern})', xml_content, re.DOTALL)
                    
                    if match:
                        style_xml = match.group(1) if match.group(1) else ""
                        full_match = match.group(0)
                        redline = (
                            f'<w:del w:id="{total_swaps*10}" w:author="{author}" w:date="{date_str}">'
                            f'<w:r>{style_xml}<w:delText>{old_xml}</w:delText></w:r></w:del>'
                            f'<w:ins w:id="{total_swaps*10+1}" w:author="{author}" w:date="{date_str}">'
                            f'<w:r>{style_xml}<w:t>{new_xml}</w:t></w:r></w:ins>'
                        )
                        xml_content = xml_content.replace(full_match, redline, 1)
                        total_swaps += 1
                        found_in_file = True

            if found_in_file:
                with open(xml_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)

        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, tmp_dir)
                    zip_out.write(full_path, rel_path)
        
        shutil.rmtree(tmp_dir)
        final_bytes = bio.getvalue()
        
        summary = f"Applied {total_swaps} surgical revisions."
        return final_bytes, EditResult(strategy="Surgical XML Surgery", summary=summary)

    except Exception as e:
        return docx_bytes, EditResult(strategy="Error", summary=str(e))
