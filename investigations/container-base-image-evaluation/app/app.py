import platform
from flask import Flask


app =  Flask(__name__)


@app.route("/health")
def health ():
    return {"status" : "ok"}

@app.route("/info")
def info():
    return {
        "system" : platform.system(),
        "architecture" : platform.machine(),
        "python" : platform.python_version(),
    }




if __name__ == "__main__" :
    app.run(host="0.0.0.0", port=8080)
