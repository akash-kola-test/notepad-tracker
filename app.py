from flask import Flask, render_template, request, jsonify
import os
import git
import threading
import platform

restricted_paths = [
    # Windows
    "c:\\",                      # Root directory
    "c:\\windows",               # Windows OS directory
    "c:\\program files",         # Installed applications
    "c:\\program files (x86)",   # 32-bit applications directory
    "c:\\users\\administrator",  # Administrator user profile
    "c:\\users\\public",         # Shared public folder

    # Linux
    "/root",                     # Root user's home directory
    "/bin",                      # Essential command binaries
    "/boot",                     # Boot files
    "/dev",                      # Device files
    "/etc",                      # System-wide configuration files
    "/lib",                      # Shared libraries
    "/proc",                     # Kernel and process information
    "/sys",                      # System information
    "/usr",                      # User programs and libraries
    "/var",                      # Variable data like logs and caches
    "/sbin",                     # System binaries
]


app = Flask(__name__)

last_saved_content = {} 

def auto_commit(file_path: str, content):
    repo_path = f"{os.path.sep}".join(file_path.split(os.path.sep)[:-1])
    file_name = file_path.split(os.path.sep)[-1]

    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    if not os.path.exists(os.path.join(repo_path, '.git')):
        repo = git.Repo.init(repo_path)  
    else:
        repo = git.Repo(repo_path)
    file_path = os.path.join(repo_path, file_name)

    if last_saved_content.get(file_name) != content:
        with open(file_path, 'w') as f:
            f.write(content)

        last_saved_content[file_name] = content

        repo.git.add(file_path)
        repo.git.commit('-m', f"Auto-saved {file_name}")
    else:
        print(f"No changes detected in {file_name}, skipping commit.")

@app.route('/')
def index():
    return render_template('index.html', platform= platform.system())

@app.route('/auto_save', methods=['POST'])
def auto_save():
    file_path = request.form['file_path']
    content = request.form['content']

    print(file_path)
    
    repo_name = f"{os.path.sep}".join(file_path.split(os.path.sep)[:-1])

    if not file_path or repo_name.lower() in restricted_paths or not content:
        return jsonify({'error': 'Invalid file path or empty content'}), 400

    threading.Thread(target=auto_commit, args=(file_path, content)).start()

    return jsonify({'success': 'File auto-saved and changes committed!'})

if __name__ == "__main__":
    app.run(debug=True)
