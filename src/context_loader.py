import os
import glob

def load_context(resource_dir="resources"):
    """
    Reads all .txt and .md files from the resources directory
    and returns them as a single string.
    """
    context_str = ""
    if not os.path.exists(resource_dir):
        return ""
        
    files = glob.glob(os.path.join(resource_dir, "*.txt")) + glob.glob(os.path.join(resource_dir, "*.md"))
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                filename = os.path.basename(file_path)
                context_str += f"\n--- File: {filename} ---\n{content}\n"
        except Exception as e:
            print(f"Error reading resource {file_path}: {e}")
            
    return context_str
