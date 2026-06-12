import sys
import os

def main():
    if len(sys.argv) < 4:
        print("Usage: python safe_replace.py <file_path> <target_string> <replacement_string>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    target = sys.argv[2].encode('utf-8')
    replacement = sys.argv[3].encode('utf-8')
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    print(f"Reading {file_path}...")
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            
        occurrences = content.count(target)
        if occurrences == 0:
            print("Target string not found in file. No changes made.")
            sys.exit(0)
            
        print(f"Found {occurrences} occurrences. Replacing...")
        content = content.replace(target, replacement)
        
        with open(file_path, 'wb') as f:
            f.write(content)
            
        print("Replacement complete and saved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
