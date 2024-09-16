from flask import Flask, render_template, request, jsonify
import os
import git
import threading

app = Flask(__name__)

repo_path = os.path.join(os.getcwd(), 'notepad_files')

if not os.path.exists(repo_path):
    os.makedirs(repo_path)

if not os.path.exists(os.path.join(repo_path, '.git')):
    repo = git.Repo.init(repo_path)  
else:
    repo = git.Repo(repo_path)

last_saved_content = {} 

def auto_commit(file_name, content):
    file_path = os.path.join(repo_path, file_name)

    if last_saved_content.get(file_name) != content:
        with open(file_path, 'w') as f:
            f.write(content)

        last_saved_content[file_name] = content

        repo.git.add(file_path)
        repo.git.commit('-m', f"Auto-saved {file_name}")
        # repo.git.push('origin', 'master')
    else:
        print(f"No changes detected in {file_name}, skipping commit.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auto_save', methods=['POST'])
def auto_save():
    file_name = request.form['file_name'] + '.txt' 
    content = request.form['content']
    
    if not file_name or not content:
        return jsonify({'error': 'Invalid file name or empty content'}), 400

    threading.Thread(target=auto_commit, args=(file_name, content)).start()

    return jsonify({'success': 'File auto-saved and changes committed!'})

if __name__ == "__main__":
    app.run(debug=True)
