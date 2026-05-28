import json, os
SKIP_DIRS={'__pycache__','.venv','venv','node_modules','.git','.pytest_cache','.ruff_cache','.mypy_cache','.deep'}
SKIP_EXT={'.pyc','.pyo','.so','.bin','.png','.jpg','.jpeg','.gif','.ico','.pdf','.zip','.tar','.gz','.db','.sqlite'}
files=[]
for root, dirs, fs in os.walk('.'):  # project root
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in fs:
        if os.path.splitext(fn)[1].lower() in SKIP_EXT:
            continue
        fp = os.path.join(root, fn)
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            continue
        rel = os.path.relpath(fp, '.')
        files.append({'path': rel, 'content': content})
payload = json.dumps({'files': files, 'commit_message': 'Scaffold layered MVP by RSBuilderAgent'})
assert len(payload) < 5000000, 'payload too large'
with open('push.json', 'w') as out:
    out.write(payload)
print(f'collected {len(files)} files, {len(payload)} bytes')
