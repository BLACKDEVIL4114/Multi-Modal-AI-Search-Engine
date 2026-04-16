import os
import sys
from lxml import etree

def validate_xml(file_path):
    try:
        with open(file_path, 'rb') as f:
            etree.fromstring(f.read())
        return True, ""
    except Exception as e:
        return False, str(e)

def validate_unpacked(unpacked_dir):
    errors = []
    for root_dir, dirs, files in os.walk(unpacked_dir):
        for file in files:
            if file.endswith('.xml'):
                full_path = os.path.join(root_dir, file)
                valid, error = validate_xml(full_path)
                if not valid:
                    errors.append(f"Invalid XML in {os.path.relpath(full_path, unpacked_dir)}: {error}")
    
    return errors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate.py <unpacked_dir>")
        sys.exit(1)
        
    unpacked_dir = sys.argv[1]
    errors = validate_unpacked(unpacked_dir)
    
    if errors:
        print("❌ Validation Failed!")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("✅ Validation Successful: All XML files are well-formed.")
