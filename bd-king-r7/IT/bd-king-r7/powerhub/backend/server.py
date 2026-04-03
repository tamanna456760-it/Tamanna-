@app.route("/pull")
def pull():
    output = run_cmd("bash powerhub/auto_sync.sh")
    return jsonify({"log": "🔄 PowerHub Pull Executed\n" + output})