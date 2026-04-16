import zipfile
import os
import sys
import argparse

def pack_docx(source_dir, output_docx):
    with zipfile.ZipFile(output_docx, 'w', compression=zipfile.ZIP_DEFLATED) as zip_ref:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)
                zip_ref.write(full_path, rel_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pack directory back into a .docx file.")
    parser.add_argument("source", help="Directory with unpacked XML files")
    parser.add_argument("output", help="Output .docx file path")
    
    args = parser.parse_args()
    pack_docx(args.source, args.output)
    print(f"Successfully packed {args.source} into {args.output}")
