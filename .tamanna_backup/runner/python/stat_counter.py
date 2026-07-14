from tamanna_auto_counter import start_auto_counter

if __name__ == "__main__":
    load_state()
    for node_name in NODES:
        threading.Thread(target=node_loop, args=(node_name,), daemon=True).start()
    threading.Thread(target=master_override, daemon=True).start()
    start_auto_counter()  # ✅ extra autonomous defense
    app.run(host="0.0.0.0", port=5000)
