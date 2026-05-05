#!/bin/bash
# KALI SURGICAL WORKFLOW v4.0
# Example usage of the Industrial Grade Office Scripts

INPUT_DOC=$1
OUTPUT_DOC=$2
STAGING_DIR="staging_$(date +%s)"

if [ -z "$INPUT_DOC" ] || [ -z "$OUTPUT_DOC" ]; then
    echo "Usage: ./run_surgery.sh input.docx output.docx"
    exit 1
fi

echo "🚀 Starting Surgical Workflow..."

# 1. Unpack
python scripts/office/unpack.py "$INPUT_DOC" "$STAGING_DIR"

# 2. Manual/Automated Edit (Example: Replace 'Old Project' with 'Kali AI')
# Note: In a real scenario, this would be a more complex sed or python edit
echo "🧬 Performing XML Surgery..."
find "$STAGING_DIR/word" -name "*.xml" -exec sed -i 's/Old Project/Kali AI/g' {} +

# 3. Validate
python scripts/office/validate.py "$STAGING_DIR"

if [ $? -eq 0 ]; then
    # 4. Pack
    python scripts/office/pack.py "$STAGING_DIR" "$OUTPUT_DOC"
    echo "✅ Surgery Complete: $OUTPUT_DOC"
else
    echo "❌ Surgery Failed: XML Validation Error"
fi

# Cleanup
rm -rf "$STAGING_DIR"
