from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Flask fonctionne ! Docker Compose OK."

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app