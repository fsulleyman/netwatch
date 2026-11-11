
from flask import Flask, render_template, jsonify
from app.monitor import get_system_metrics

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "application": "NetWatch"
    })


@app.route("/api/metrics")
def metrics():
    try:
        data = get_system_metrics()
        return jsonify(data)
    except Exception as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
