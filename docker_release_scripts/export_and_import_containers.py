import os
import subprocess
import sys

from docker_release_scripts.release_backup_and_restore_constants import SQL_CONTAINER_IMG, EXPORTED_CONTAINRS_PATH, \
    ANGULAR_CONTAINER_IMG, FLASK_CONTAINER_IMG, SQL_CONTAINER_NAME, ANGULAR_CONTAINER_NAME, FLASK_CONTAINER_NAME


class ExportAndImportController:
    @staticmethod
    def export_containers():
        if not os.path.exists(EXPORTED_CONTAINRS_PATH):
            os.makedirs(EXPORTED_CONTAINRS_PATH)

        export_mysql_container_cmd = f'docker save --output {EXPORTED_CONTAINRS_PATH}{SQL_CONTAINER_NAME}.tar {SQL_CONTAINER_IMG}'
        export_angular_container_cmd = f'docker save --output {EXPORTED_CONTAINRS_PATH}{ANGULAR_CONTAINER_NAME}.tar {ANGULAR_CONTAINER_IMG}'
        export_flask_container_cmd = f'docker save --output {EXPORTED_CONTAINRS_PATH}{FLASK_CONTAINER_NAME}.tar {FLASK_CONTAINER_IMG}'

        subprocess.run(export_mysql_container_cmd, shell=True)
        subprocess.run(export_angular_container_cmd, shell=True)
        subprocess.run(export_flask_container_cmd, shell=True)

    @staticmethod
    def get_import_containers_command():
        assert len(sys.argv) == 3, 'You need to provide the path to the .tar containers after import'
        destination = sys.argv[2]

        return f"""
docker load --input {destination}/{SQL_CONTAINER_IMG}.tar
docker load --input {destination}/{ANGULAR_CONTAINER_IMG}.tar
docker load --input {destination}/{FLASK_CONTAINER_IMG}.tar"""

    @staticmethod
    def get_scp_files_to_destination_command():
        REMOTE_USER = 'kostadin'
        REMOTE_ADDRESS = '192.168.1.6'
        REMOTE_PATH = '/drives/D/rumen_website_deployment/'

        return f"""
'Execute this command in the cmd to transfer the containers and then call the script with import option'
scp -r -P 22 D:\\Coding\\rumen_website_backend\\docker_release_scripts\\* {REMOTE_USER}@{REMOTE_ADDRESS}:{REMOTE_PATH}
scp -P 22 {EXPORTED_CONTAINRS_PATH}\\* {REMOTE_USER}@{REMOTE_ADDRESS}:{REMOTE_PATH}
"""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        if option == 'import':
            print(ExportAndImportController.get_import_containers_command())
        elif option == 'export':
            ExportAndImportController.export_containers()
            print(ExportAndImportController.get_scp_files_to_destination_command())
        else:
            print("No valid option was provided. Please specify import or export for the first argument.")
    else:
        print("No arguments provided. Please specify import or export for the first argument.")
