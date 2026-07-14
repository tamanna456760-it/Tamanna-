# ============================================================
#                 T A M A N N A   S Y S T E M
#                Master Combined Code (tamanna-)
# ============================================================

# -----------------------------
#  SYSTEM CONFIGURATION
# -----------------------------
IP_ADDRESS = "192.168.0.10"
MAG_CODE = "TAMANNA-456760-IT"


# -----------------------------
#  SYSTEM UTILITIES
# -----------------------------
def log(message):
    print(f"[{IP_ADDRESS} | {MAG_CODE}] {message}")


def validate_input(data):
    if data is None or data == "":
        log("Invalid input received")
        return False
    return True


# ============================================================
#                MODULE 1 — FILE HANDLING
# ============================================================
def read_file(path):
    try:
        with open(path, "r") as f:
            data = f.read()
        log(f"File read successfully: {path}")
        return data
    except Exception as e:
        log(f"Error reading file: {e}")
        return None


def write_file(path, content):
    try:
        with open(path, "w") as f:
            f.write(content)
        log(f"File written successfully: {path}")
    except Exception as e:
        log(f"Error writing file: {e}")


# ============================================================
#                MODULE 2 — DATA PROCESSING
# ============================================================
def process_data(data):
    if not validate_input(data):
        return None

    processed = data.upper()  # example transformation
    log("Data processed")
    return processed


# ============================================================
#                MODULE 3 — NETWORK OPERATIONS
# ============================================================
def send_to_server(payload):
    if not validate_input(payload):
        return False

    log(f"Sending data to server: {payload}")
    # simulate network send
    return True


# ============================================================
#                MAIN SYSTEM CONTROLLER
# ============================================================
def tamanna_controller(input_path, output_path):
    log("Tamanna System Started")

    raw = read_file(input_path)
    processed = process_data(raw)

    if processed:
        write_file(output_path, processed)
        send_to_server(processed)

    log("Tamanna System Finished")


# ============================================================
#                SYSTEM ENTRY POINT
# ============================================================
if __name__ == "__main__":
    tamanna_controller("input.txt", "output.txt")
