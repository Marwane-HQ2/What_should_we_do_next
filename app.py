import time, json, re
from flask import Flask, request, jsonify, render_template, redirect, url_for
from hashlib import blake2b

app = Flask("app")

# ----------------------------------------------------

def load_from_file():
    try:
        with open('todos.json', 'r') as f:
            # Lire le fichier JSON et le convertir en dictionnaire Python
            return json.load(f)
    except FileNotFoundError:
        # Si le fichier n'existe pas, retourner un dictionnaire vide
        return {}

def save_to_file():
    with open('todos.json', 'w') as f:
        json.dump(DATAS, f, indent=4)
    return

def hash(string):
    h = blake2b()
    h.update(string.encode())
    return h.hexdigest()

# GENERATE UNIQUE IDs
def generate_timestamp_id():
    return str(int(time.time() * 1000000))

# ----------------------------------------------------
DATAS = load_from_file()

# ----------------------------------------------------
# THE ROUTE THAT ALLOWS TO ACCESS THE HOME PAGE
@app.route("/")
def start():
    return render_template('home.html')

# THE ROUTE THAT ALLOWS TO LOGIN
@app.route("/login")
def login():
    message, error = request.args.get("message"), request.args.get("error")
    return render_template("login.html", message=message if message else "", error= error if error else "")

# THE ROUTE THAT ALLOWS TO REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

# THE REQUEST THAT "POST" THE INFORMATIONS OF THE NEWLY REGISTERED USER
@app.route("/new-user", methods=["GET", "POST"])
def create_new_user():
    username, password = request.args.get("un"), request.args.get("p")
    
    if username in DATAS:
        return "USER_EXISTS_ALREADY", 200
    
    regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?!.*\s).{8,}$"
    if not re.match(regex, password):
        return "NON_CONFORM_PASSWORD", 200
    
    DATAS[username] = { # CREATE A NEW ACCOUNT
        "password": hash(password),
        "todos": {

        }
    }
    save_to_file()
    return redirect(url_for("login", message="You have been successfully registrated ! Login !")), 301 # UTILISER LE CODE 301 QUAND ON REDIRIGE DE FACON PERMANENTE


# USED TO LOGIN
@app.route("/give-access")
def give_access():
    username, password = request.args.get("un"), hash(request.args.get("p"))
    error = "The username doesn't match with any account"

    if username in DATAS:
        if password == DATAS[username]["password"]:
            return redirect(url_for('dashboard', username=username))
        
        error = "Wrong password"

    return redirect(url_for("login", error=error, message="")), 301

# THE ROUTE THAT ALLOWS TO VISIT DASHBOARD
@app.route('/dashboard/<username>', methods=['GET'])
def dashboard(username):
    if username in DATAS:
        todo_id = request.args.get("id", default=False)
        if todo_id:
            data = False
            nb = 0
            if todo_id in DATAS[username]["todos"]:
                data = DATAS[username]["todos"][todo_id]
                for e in data["tasks"]:
                    if e["completed"]:
                        nb += 1
                return render_template('dashboard.html', username=username, data=data, length_tasks=len(data["tasks"]), id=todo_id, nb_completed=nb)
        return render_template('dashboard_loged.html', username=username, todo=DATAS[username]["todos"])
    return redirect(url_for("start"))


























# ERROR_DICT = {
#     'oopsie_id_dashboard': ("Non matching ID", "Can't find your todo list ! \
# Correct the link you used or create a new todo list !")
# }

# @app.route('/oopsie/<error_id>', methods=['GET'])
# def oopsie(error_id):
#     error_short, error_message = ERROR_DICT[error_id]
#     return render_template('oopsie.html', error_short=error_short, error_message=error_message)


# THE ROUTE THAT ALLOWS TO CREATE A TODOLIST
@app.route("/create-todo/<username>", methods=["GET", "POST"]) # THE POST REQUEST
def create_todo(username):    
    title, goal, deadline = request.args.get("title"), request.args.get("goal"), request.args.get("deadline")
    ID = generate_timestamp_id()

    data = {
        "todo_id": ID,
        "title": title,
        "deadline": deadline,
        "tasks": [{
            'title': 'Reach my goal',
            'description': 'The final boss',
            "completed": False,
            "index": 0,
            }],
        "goal": goal,
        "registered": True,
    }
    DATAS[username]["todos"][ID] = data
    save_to_file()
    
    return redirect(url_for('dashboard', username=username)), 301


# OK !
@app.route("/update-task/<username>/<todo_id>/<task_index>/<status>", methods=["GET", "POST"])
def update_task(username, todo_id, task_index, status):
    DATAS[username]["todos"][todo_id]["tasks"][int(task_index)]["completed"] = {"true": True, "false": False}[status]
    save_to_file()
    return redirect(url_for('dashboard', username=username)), 301

# OK !
@app.route("/get-tasks/<username>/<todo_id>")
def get_tasks(username, todo_id):
    data = DATAS[username]["todos"][todo_id]["tasks"]
    return jsonify(data)

@app.route("/create-task/<username>/<todo_id>", methods=["GET", "POST"])
def create_task(username, todo_id):
    title, description = request.args.get("title"), request.args.get("description")
    newTask = {
        "title": title,
        "description": description,
        "completed": False,
        "index": len(DATAS[username]["todos"][todo_id]["tasks"])
    }
    DATAS[username]["todos"][todo_id]["tasks"].append(newTask)
    save_to_file()
    return redirect(f"/dashboard/{username}?id={todo_id}"), 301

if __name__ == "__main__":
    app.run()
