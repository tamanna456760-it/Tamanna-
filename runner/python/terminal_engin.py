# Tamanna Terminal Connection Engine
import subprocess


def run_terminal_command(command):
    try:
        output = subprocess.check_output(command, shell=True)
        print(f"[TERMINAL] {output.decode()}")
    except Exception as e:
        print(f"[TERMINAL ERROR] {e}")

if __name__ == "__main__":
    run_terminal_command("echo Tamanna Terminal Connected")
