from ai_engine import ai_status
from powerhub import powerhub_status

def main():
    print("Tamanna AI System Starting...")
    print(ai_status())
    print(powerhub_status())

if __name__ == "__main__":
    main()