import os

# This script would ideally be part of the build process to
# update the injector or agent code with specific class names if they are known.
# For now, AgentMain.java uses a broad approach based on package prefix.

def update_broad_injector():
    path = "java_tools/src/BroadInjector.java"
    if not os.path.exists(path):
        print(f"{path} not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Update to use com.applicationjp.JPTranslationPlugin.translate()
    new_code = 'String injectionCode = "{ $" + paramIndex + " = com.applicationjp.JPTranslationPlugin.translate($" + paramIndex + "); }";'

    # Very crude replacement for demo
    if "TR.containsKey" in content:
        import re
        content = re.sub(r'String injectionCode = "{"\s*\+\s*"  if \($.*?com\.applicationjp\.JPTranslationPlugin\.TR\.get\($.*?\);"\s*\+\s*"  }"\s*\+\s*"}";', new_code, content, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated BroadInjector.java to use advanced translation logic.")

if __name__ == "__main__":
    update_broad_injector()
