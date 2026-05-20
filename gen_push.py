import json
import os

def generate_push_data():
    """Generate push data for test files."""
    files = []
    
    # Add test_api.py
    test_api_path = "/workspace/tests/test_api.py"
    if os.path.exists(test_api_path):
        with open(test_api_path, 'r', encoding='utf-8') as f:
            test_content = f.read()
        files.append({
            'path': 'tests/test_api.py',
            'content': test_content
        })
    
    # Add GitHub Actions workflow
    workflow_path = "/workspace/.github/workflows/test.yml"
    if os.path.exists(workflow_path):
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow_content = f.read()
        files.append({
            'path': '.github/workflows/test.yml',
            'content': workflow_content
        })
    
    return files

if __name__ == "__main__":
    # Generate files list
    files = generate_push_data()
    
    # Create push data
    push_data = {
        'files': files,
        'commit_message': 'Improve: Add comprehensive test suite and GitHub Actions CI'
    }
    
    # Save to file
    with open('/tmp/push.json', 'w') as f:
        json.dump(push_data, f, indent=2)
    
    print(f"Generated push data with {len(files)} files")
    print("Files included:")
    for file_info in files:
        print(f"  - {file_info['path']}")
    
    print("\nPush data saved to /tmp/push.json")