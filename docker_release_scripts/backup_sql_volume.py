import subprocess
import datetime
import os

from docker_release_scripts.release_backup_and_restore_constants import DATETIME_FORMAT, BACKUP_PATH, VOLUME_PATH, \
    SQL_CONTAINER_IMG, BACKUP_PREFIX, BACKUP_POSTFIX


class BackupAndRestoreController:
    @staticmethod
    def create_backup():
        if not os.path.exists(BACKUP_PATH):
            os.makedirs(BACKUP_PATH)

        backup_time = datetime.datetime.now().strftime(DATETIME_FORMAT)
        backup_filename = f"{BACKUP_PREFIX}{backup_time}{BACKUP_POSTFIX}"

        docker_cmd = f'docker run --rm --volumes-from {SQL_CONTAINER_IMG} -v {BACKUP_PATH}:/backup ubuntu tar -cvzf /backup/{backup_filename} -C {VOLUME_PATH} ./'
        subprocess.run(docker_cmd, shell=True)

        print(f"Backup created: {BACKUP_PATH}\\{backup_filename}")

    @staticmethod
    def delete_older_backups(days=31):
        current_date = datetime.datetime.now()
        too_old_date = current_date - datetime.timedelta(days=days)

        files = [file for file in os.listdir(BACKUP_PATH) if file.endswith(BACKUP_POSTFIX)]
        if len(files) < days:
            print("Did not delete any backups, as there are backups from throughout the last week")
            return
        for file in files:
            file_date_str = file.strip(BACKUP_PREFIX).strip(BACKUP_POSTFIX)
            file_date = datetime.datetime.strptime(file_date_str, DATETIME_FORMAT)

            if file_date < too_old_date:
                os.remove(os.path.join(BACKUP_PATH, file))
                print(f"Deleted {file}")

    @staticmethod
    def restore_from_backup(file_name):
        assert file_name in os.listdir(BACKUP_PATH), \
            "No such backup exists, please make sure to end the backup with .tar.gz"

        docker_cmd = f'docker run --rm --volumes-from {SQL_CONTAINER_IMG} -v {BACKUP_PATH}:/backup ubuntu bash -c "cd {VOLUME_PATH} && tar xvf /backup/{file_name} --strip 1"'
        subprocess.run(docker_cmd, shell=True)

        restart_docker_containers_cmd = f'docker compose restart'

        subprocess.run(restart_docker_containers_cmd, shell=True)

        print(f"Backup restored from: {file_name}")


if __name__ == "__main__":
    BackupAndRestoreController.create_backup()
    BackupAndRestoreController.delete_older_backups()
