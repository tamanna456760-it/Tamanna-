# Tamanna Core Runner
import monitoring_engin, run_engin, backup_engin

def main():
    monitoring_engin.MonitoringEngine().log("TamannaCore", True)
    run_engin.run()
    backup_engin.backup_file("engin.py", "backup/engin.py")

if __name__ == "__main__":
    main()
