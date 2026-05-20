import json
import os
import glob

def generate_push_data():
    """Generate push data for all files in the project."""
    files = []
    
    # Walk through all files in the project directory
    for root, _, fs in os.walk('/workspace/proj'):
        for fn in fs:
            fp = os.path.join(root, fn)
            
            # Skip __pycache__ directories and .pyc files
            if '__pycache__' in fp or fn.endswith('.pyc'):
                continue
            
            # Skip .git directory if exists
            if '.git' in fp:
                continue
            
            # Skip .DS_Store files
            if fn == '.DS_Store':
                continue
            
            # Read file content
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Convert to relative path from project root
                relative_path = fp.replace('/workspace/proj/', '')
                
                files.append({
                    'path': relative_path,
                    'content': content
                })
                
            except Exception as e:
                print(f"Error reading {fp}: {e}")
    
    return files

if __name__ == "__main__":
    # Generate files list
    files = generate_push_data()
    
    # Create push data
    push_data = {
        'files': files,
        'commit_message': 'Refactor: Extract logic into thinner functions and improve type hints in task_service.py'
    }
    
    # Save to file
    with open('/tmp/push.json', 'w') as f:
        json.dump(push_data, f, indent=2)
    
    print(f"Generated push data with {len(files)} files")
    print("Files included:")
    for file_info in files:
        print(f"  - {file_info['path']}")
    
    print("\nPush data saved to /tmp/push.json")