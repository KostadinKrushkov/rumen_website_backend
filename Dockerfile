FROM python:3.8
WORKDIR /python-docker


# Copying the SSL certificates
RUN mkdir -p ./project/git_ignored_temp
COPY ./project/git_ignored_temp/official_rumenplamenovart.com-2023-02-09.pem /python-docker/project/git_ignored_temp/
COPY ./project/git_ignored_temp/rumenplamenovart.com-2023-02-09.key /python-docker/project/git_ignored_temp/


# ---- Configuration for sql driver ----
# UPDATE APT-GET
RUN apt-get update

# PYODBC DEPENDENCIES
RUN apt-get install -y tdsodbc unixodbc-dev
RUN apt install unixodbc -y
RUN apt-get clean -y
ADD odbcinst.ini /etc/odbcinst.ini

# UPGRADE pip3
RUN pip3 install --upgrade pip

# DEPENDECES FOR DOWNLOAD ODBC DRIVER
RUN apt-get install apt-transport-https
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update

# INSTALL ODBC DRIVER
RUN ACCEPT_EULA=Y apt-get install msodbcsql17 --assume-yes

# CONFIGURE ENV FOR /bin/bash TO USE MSODBCSQL17
RUN echo "export PATH="$PATH:/opt/mssql-tools/bin"" >> ~/.bash_profile
RUN echo "export PATH="$PATH:/opt/mssql-tools/bin"" >> ~/.bashrc
# ---- End of configuration ----


# Installing the necessary packages for the flask application
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "gunicorn", "-w", "5", "--preload", "-b 0.0.0.0:5000", "--chdir", "/python-docker/project", "--certfile", "/python-docker/project/git_ignored_temp/official_rumenplamenovart.com-2023-02-09.pem", "--keyfile", "/python-docker/project/git_ignored_temp/rumenplamenovart.com-2023-02-09.key", "--timeout", "600", "app:app" ]


# ---- RUNNING WITH DOCKER ----
# build image with
# docker build -t rocazzar/rumen-plamenov-website-backend .

# run image with
# docker run -d -it -p 5000:5000 --env-file ./setup/sql_server_env.list --name rumen-plamenov-website-backend rocazzar/rumen-plamenov-website-backend

# run with debug:
# docker run -d -it -p 5000:5000 -p 5678:5678 --env-file ./setup/sql_server_env.list --name rumen-plamenov-website-backend rocazzar/rumen-plamenov-website-backend

#####
# run sql server
# docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=<env config password>" -p 1433:1433 -v sqlvolume:/var/opt/mssql -d --name mysqlsrv mcr.microsoft.com/mssql/server:2019-latest

