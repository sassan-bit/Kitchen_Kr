import os

def fix_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig strips BOM
            content = f.read()
        # Reverses double-encoding: UTF-8 bytes → read as cp1252 → written as UTF-8
        fixed = content.encode('latin-1').decode('utf-8')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"Fixed: {file_path}")
    except Exception as e:
        print(f"Skipped {file_path}: {e}")

for root, dirs, files in os.walk('templates'):
    dirs[:] = [d for d in dirs if d != 'venv']
    for file in files:
        if file.endswith('.html'):
            fix_file(os.path.join(root, file))

print("Done!")
