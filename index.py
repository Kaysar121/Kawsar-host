from app import app
from flask import jsonify

@app.route('/')
def index():
    return jsonify({"message": "HOSTING WEBSITE IS ACTIVE", "status": "active"})

if __name__ == '__main__':
    app.run()