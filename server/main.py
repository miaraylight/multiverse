import os
import secrets

from dotenv import load_dotenv

from flask import Flask, jsonify
from flask import url_for, request, redirect, session
from werkzeug.serving import run_simple
from sqlite import SQLite

from Crypto.Hash import SHA256

from langchain.schema import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

STATUS_OK = "ok"
STATUS_ERROR = "error"

# Configure flask app
app = Flask(__name__)
app.debug = True
app.secret_key = secrets.token_urlsafe(32)

# Configure database
local_db = SQLite()
local_db.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db"))

# Build model list
load_dotenv()

MODELS = {
    1: {
        "provider": "OpenAI",
        "model": "gpt-4",
        "instance": ChatOpenAI(model="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY")),
    },
    2: {
        "provider": "Google",
        "model": "gemini-pro",
        "instance": ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv('GOOGLE_API_KEY'))
    },
    3: {
        "provider": "Anthropic",
        "model": "claude-3-opus-20240229",
        "instance": ChatAnthropic(model="claude-3-opus-20240229", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
    }
}


###############################################################################
# Helper decorators to check errors and logged state
###############################################################################
def check_logged():
    """
    Decorator to check if user is logged
    """

    def inner(func):
        def wrapper(*args, **kwargs):
            if "username" in session:
                return func(*args, **kwargs)
            else:
                return jsonify({
                    "status": STATUS_ERROR,
                    "error": "Request error: user is not logged"
                })

        wrapper.__name__ = f"check_login_wrapper_{func.__name__}"
        return wrapper

    return inner


def handle_errors():
    def inner(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    "status": STATUS_ERROR,
                    "error": f"Internal error: {e}"
                })

        wrapper.__name__ = f'handle_errors_wrapper_{func.__name__}'
        return wrapper

    return inner


###############################################################################
# Authorization functions (register, login, logout)
###############################################################################
@app.route("/auth/register", methods=["POST"])
@handle_errors()
def auth_register():
    request_json = request.get_json()

    users = local_db.select('users', where={'username': request_json['username']})

    if len(users) != 0:
        return jsonify({
            'status': STATUS_ERROR,
            'error': 'A user with same user name already exists, try another'
        })

    pass_hash = SHA256.new(bytes(request_json['password'], encoding='utf-8')).hexdigest()

    local_db.insert('users', values={
        'username': request_json['username'],
        'password': pass_hash,
        'name': request_json['name'] if 'name' in request_json else '',
        'permissions_id': 1,
    })

    return jsonify({
        'status': STATUS_OK
    })


@app.route("/auth/login", methods=["POST"])
@handle_errors()
def auth_login():
    request_json = request.get_json()

    if "username" not in request_json or "password" not in request_json:
        return jsonify({
            "status": "error",
            "error": "Login error: no user name or password was provided"
        })

    pass_hash = SHA256.new(bytes(request_json['password'], encoding='utf-8')).hexdigest()

    users = local_db.select("users", where={
        "username": request_json["username"],
        "password": pass_hash
    })

    if len(users) == 0:
        return jsonify({
            "status": STATUS_ERROR,
            "error": "Invalid login or password",
        })

    session["username"] = users[0]["username"]
    session["id"] = users[0]["id"]

    return jsonify({
        "status": STATUS_OK
    })


@app.route("/auth/logout", methods=["GET"])
@handle_errors()
def auth_logout():
    session.pop("username", None)
    session.pop("id", None)

    return jsonify({
        "status": STATUS_OK
    })


###############################################################################
# Chat functions
###############################################################################
@app.route("/chat/list", methods=["GET"])
@check_logged()
@handle_errors()
def chat_list():
    result = {
        "status": STATUS_OK,
        "chats": []
    }

    chats = local_db.select("chats", where={"user_id": session["id"]})

    for chat in chats:
        result["chats"].append({
            "id": chat["id"],
            "title": chat["title"],
        })

    return jsonify(result)


@app.route("/chat/create", methods=["POST"])
@check_logged()
@handle_errors()
def chat_create():
    request_json = request.get_json()

    chat_id = local_db.insert("chats", values={
        "user_id": session["id"],
        "title": request_json["title"]
    })

    session["chat_id"] = chat_id
    session["history"] = []

    return jsonify({
        "status": STATUS_OK
    })


@app.route("/chat/edit", methods=["POST"])
@check_logged()
@handle_errors()
def chat_edit():
    request_json = request.get_json()

    chats = local_db.select("chats", where={
        "id": request_json["chat_id"],
        "user_id": session["id"],
    })

    if len(chats) == 0:
        return jsonify({
            "status": STATUS_ERROR,
            "error": f"Error changing chat data: chat with ID {request_json['chat_id']} not found"
        })

    local_db.update("chats",
                    values={"title": request_json["title"]},
                    where={"id": request_json["chat_id"], "user_id": session["id"]}
                    )

    return jsonify({
        "status": STATUS_OK
    })


@app.route("/chat/delete", methods=["POST"])
@check_logged()
@handle_errors()
def chat_delete():
    request_json = request.get_json()

    chats = local_db.select("chats", where={"id": request_json["chat_id"], "user_id": session["id"]})

    if len(chats) == 0:
        return jsonify({
            "status": STATUS_ERROR,
            "error": "Error deleting chat: chat with ID {} not found"
        })

    local_db.delete("chats", where={"id": request_json["chat_id"], "user_id": session["id"]})

    if "chat_id" in session and session["chat_id"] == request_json["chat_id"]:
        session.pop("chat_id", None)
        session.pop("history", None)

    return jsonify({
        "status": STATUS_OK
    })


@app.route("/chat/get", methods=["POST"])
@check_logged()
@handle_errors()
def chat_get():
    request_json = request.get_json()

    chats = local_db.select("chats", where={"id": request_json["chat_id"], "user_id": session["id"]})

    if len(chats) == 0:
        return jsonify({
            "status": STATUS_ERROR,
            "error": f"Error getting chat: chat with ID {request_json['chat_id']} not found"
        })

    # Initialize session and restore history from the database
    session["chat_id"] = request_json["chat_id"]
    session["history"] = []

    messages = local_db.select("chat_messages", where={"chat_id": request_json["chat_id"]})
    for message in messages:
        session["history"].append({
            "role": message["role"],
            "message": message["message"]
        })

    return jsonify({
        "status": STATUS_OK,
        "id": request_json["chat_id"],
        "title": chats[0]["title"],
        "messages": session["history"]
    })


@app.route("/chat/send", methods=["POST"])
@check_logged()
@handle_errors()
def chat_send():
    request_json = request.get_json()

    if "model_id" not in request_json:
        return jsonify({
            "status": STATUS_ERROR,
            "error": "Error sending message: model ID is not provided"
        })

    if request_json["model_id"] not in MODELS.keys():
        return jsonify({
            "status": STATUS_ERROR,
            "error": f"Model with ID {request_json['model_id']} not found"
        })

    if "chat_id" not in session:
        return jsonify({
            "status": STATUS_ERROR,
            "error": "Error: no chat selected"
        })

    local_db.insert("chat_messages", values={
        "chat_id": session["chat_id"],
        "message": request_json["message"],
        "role": "user"
    })
    session["history"].append({
        "role": "user",
        "message": request_json["message"]
    })

    model = MODELS[request_json["model_id"]]

    history = []
    for message in session["history"]:
        if message["role"] == "user":
            history.append(HumanMessage(message["message"]))
        else:
            history.append(AIMessage(message["message"]))

    response = model["instance"].invoke(history)

    local_db.insert("chat_messages", values={
        "chat_id": session["chat_id"],
        "message": response.content,
        "role": "assistant",
    })
    session["history"].append({
        "role": "assistant",
        "message": response.content
    })

    return jsonify({
        "status": STATUS_OK,
        "response": response.content
    })


###############################################################################
# Models
###############################################################################
@app.route("/models/list", methods=["GET"])
@check_logged()
@handle_errors()
def models_list():
    result = {
        "status": STATUS_OK,
        "models": []
    }

    for mid in MODELS.keys():
        result["models"].append({
            "id": mid,
            "provider": MODELS[mid]["provider"],
            "model": MODELS[mid]["model"],
        })

    return jsonify(result)


###############################################################################
# Static redirections
###############################################################################
@app.route('/images/<path:filename>')
def images_dir(filename):
    return redirect(url_for('static', filename=f'images/{filename}'))


@app.route('/css/<path:filename>')
def css_dir(filename):
    return redirect(url_for('static', filename=f'css/{filename}'))


@app.route('/javascript/<path:subpath>')
@app.route('/js/<path:subpath>')
def js_dir(subpath):
    return redirect(url_for('static', filename=f'js/{subpath}'))


if __name__ == '__main__':
    run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True, use_evalex=True, threaded=True)
