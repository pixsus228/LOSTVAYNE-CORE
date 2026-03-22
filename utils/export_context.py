import os
from datetime import datetime


def export_project():
    project_root = "."
    bridge_dir = os.path.join(os.path.expanduser("~"), "Desktop", "JARVIS_BRIDGE")
    os.makedirs(bridge_dir, exist_ok=True)

    private_files = [".env", "credentials.py", "secrets.json", "lostvayne_brain.db"]
    exclude_dirs = [".venv", ".git", "__pycache__", "backups"]
    context = ""

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py") or file == ".gitignore":
                if file not in private_files:
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            context += f"\n{'=' * 20}\nFILE: {path}\n{'=' * 20}\n{f.read()}\n"
                    except:
                        continue

    # Видаляю старі зліпки перед записом нового
    for old in os.listdir(bridge_dir):
        try:
            os.remove(os.path.join(bridge_dir, old))
        except:
            pass

    timestamp = datetime.now().strftime("%H-%M-%S")
    full_path = os.path.join(bridge_dir, f"full_context_{timestamp}.txt")

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(context)
    print(f"✅ Сер, повний зліпок готовий: {full_path}")


if __name__ == "__main__":
    export_project()