import zipfile
import os
import sys
import argparse
import xml.dom.minidom
from lxml import etree

def merge_runs(root):
    """
    Finds consecutive <w:r> elements with identical properties (<w:rPr>)
    and merges them to make text searching easier.
    """
    W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    
    for p in root.xpath("//w:p", namespaces={"w": W_NS.strip("{}")}):
        runs = p.xpath("w:r", namespaces={"w": W_NS.strip("{}")})
        if len(runs) < 2:
            continue
            
        i = 0
        while i < len(runs) - 1:
            r1 = runs[i]
            r2 = runs[i+1]
            
            # Extract rPr (Run Properties)
            rPr1 = r1.find(f"{W_NS}rPr")
            rPr2 = r2.find(f"{W_NS}rPr")
            
            rPr1_str = etree.tostring(rPr1) if rPr1 is not None else b""
            rPr2_str = etree.tostring(rPr2) if rPr2 is not None else b""
            
            # If properties match, merge r2 into r1
            if rPr1_str == rPr2_str:
                t1 = r1.find(f"{W_NS}t")
                t2 = r2.find(f"{W_NS}t")
                
                if t1 is not None and t2 is not None:
                    t1.text = (t1.text or "") + (t2.text or "")
                    # Preserve whitespace if needed
                    if t1.text.startswith(" ") or t1.text.endswith(" "):
                        t1.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                    
                    p.remove(r2)
                    runs.pop(i+1)
                    continue
            i += 1

def unpack_docx(docx_path, output_dir, merge=True):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            extracted_path = zip_ref.extract(file_info, output_dir)
            
            if extracted_path.endswith('.xml') or extracted_path.endswith('.rels'):
                try:
                    with open(extracted_path, 'rb') as f:
                        xml_content = f.read()
                    
                    root = etree.fromstring(xml_content)
                    
                    if merge and extracted_path.endswith('document.xml'):
                        merge_runs(root)
                    
                    # Pretty print for manual editing
                    pretty_xml = etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True)
                    
                    with open(extracted_path, 'wb') as f:
                        f.write(pretty_xml)
                except Exception as e:
                    print(f"Warning: Could not process {extracted_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unpack DOCX to pretty-printed XML for editing.")
    parser.add_argument("docx", help="Path to source .docx file")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("--merge-runs", type=bool, default=True, help="Merge adjacent runs with same properties")
    
    args = parser.parse_args()
    unpack_docx(args.docx, args.output, args.merge_runs)
    print(f"Successfully unpacked {args.docx} to {args.output}")
