# Tamanna Core Runner
import backup_engin
import monitoring_engin
import run_engin


def main():
    monitoring_engin.MonitoringEngine().log("TamannaCore", True)
    run_engin.run()
    backup_engin.backup_file("engin.py", "backup/engin.py")

if __name__ == "__main__":
    main()
