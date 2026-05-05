import subprocess
import argparse
import sys
import os

def call_soffice(command_args):
    # Try to find soffice. On Windows, it's often in Program Files.
    soffice_path = "soffice" # Assume it's in PATH
    
    # Common Windows paths if not in PATH
    potential_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    
    for p in potential_paths:
        if os.path.exists(p):
            soffice_path = p
            break
            
    cmd = [soffice_path] + command_args
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error calling soffice: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'soffice' (LibreOffice) not found. Please install LibreOffice and add it to your PATH.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LibreOffice Headless Wrapper")
    parser.add_argument("--convert-to", help="Target format (e.g. docx, pdf)")
    parser.add_argument("file", help="Source file")
    parser.add_argument("--outdir", default=".", help="Output directory")
    
    args, unknown = parser.parse_known_args()
    
    cmd_args = ["--headless"]
    if args.convert_to:
        cmd_args += ["--convert-to", args.convert_to]
    
    cmd_args += ["--outdir", args.outdir]
    cmd_args += [args.file]
    
    # Add any other arguments passed
    cmd_args += unknown
    
    call_soffice(cmd_args)
