import sys

from docker_release_scripts.backup_sql_volume import BackupAndRestoreController

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
        BackupAndRestoreController.restore_from_backup(file_name)
    else:
        print("No arguments provided. Write the name of the backup you wish to restore from ending with .tar.gz")
