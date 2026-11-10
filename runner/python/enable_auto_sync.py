"""Opt-in legacy monitor activation; Git auto-commit and cloud backup stay disabled."""
import os


def main():
    if os.environ.get("TAMANNA_ENABLE_LEGACY_MONITOR") != "1":
        print("Legacy monitor disabled; set TAMANNA_ENABLE_LEGACY_MONITOR=1 to opt in")
        return

    try:
        import builder
    except ImportError as error:
        raise RuntimeError("Legacy builder module is not installed") from error

    builder.enable_auto_sync(
        git_auto_commit=False,
        cloud_backup=False,
        real_time_monitoring=True,
    )


if __name__ == "__main__":
    main()
