import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

APPLICATION_CORE_DIR = os.environ.get("APPLICATION_CORE_DIR", r"C:\Program Files (x86)\Acme Corp\Application\application-core")
WORKSPACE_DIR = os.environ.get("WORKSPACE_DIR", ".")
