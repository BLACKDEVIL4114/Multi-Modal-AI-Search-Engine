import os
import sys
import argparse
from lxml import etree
from datetime import datetime

def add_comment(unpacked_dir, comment_id, text, author="Claude", parent_id=None):
    W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    nsmap = {"w": W_NS.strip("{}")}
    
    comments_path = os.path.join(unpacked_dir, "word", "comments.xml")
    
    # Ensure comments.xml exists
    if not os.path.exists(comments_path):
        root = etree.Element(f"{W_NS}comments", nsmap=nsmap)
    else:
        with open(comments_path, 'rb') as f:
            root = etree.fromstring(f.read())
            
    # Create the comment element
    comment = etree.SubElement(root, f"{W_NS}comment", {
        f"{W_NS}id": str(comment_id),
        f"{W_NS}author": author,
        f"{W_NS}date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        f"{W_NS}initials": author[0] if author else "A"
    })
    
    p = etree.SubElement(comment, f"{W_NS}p")
    r = etree.SubElement(p, f"{W_NS}r")
    t = etree.SubElement(r, f"{W_NS}t")
    t.text = text
    
    with open(comments_path, 'wb') as f:
        f.write(etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True))
    print(f"Added comment {comment_id} to word/comments.xml")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add comments to unpacked DOCX XML.")
    parser.add_argument("dir", help="Unpacked directory")
    parser.add_argument("id", type=int, help="Comment ID")
    parser.add_argument("text", help="Comment text")
    parser.add_argument("--author", default="Claude", help="Comment author")
    
    args = parser.parse_args()
    add_comment(args.dir, args.id, args.text, args.author)
