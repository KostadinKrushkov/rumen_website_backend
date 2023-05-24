# Rumen Plamenov art gallery REST API
_Visit [rumenplamenovart.com](https://rumenplamenovart.com/) to see final result_

This repo is the REST API for the art gallery website including the database design.
To view the UI code, you can visit https://github.com/KostadinKrushkov/art_gallery_website

Technologies used for this project
- Frontend Development: Angular (Typescript), HTML, CSS
- Backend Development: Python3 + Flask + SQLAlchemy
- SQL server + SQL Management Studio
- Deployment: Docker + docker-compose
- HTTP/WSGI servers: Nginx/Gunicorn
- Testing: mostly integration tests with pytest, and some unit testing

---

# To configure networking for running the containers
- First you have to set a static ip address e.g 213.91.236.77
- Next change your LAN ip address to a static one instead of VIA dhcp e.g. 192.168.1.10 -> router (192.168.1.1)
- Next setup a port forwarding rule for all ports you need through the route port forwarding (https://portforward.com/cambridge-industries-group/gpon-g-93rg1/)
- Make sure your port forwawding is working by running an application or a port e.g. 5000 and pinging that port (e.g. via https://www.yougetsignal.com/tools/open-ports/)
- Make sure you can reach your own static ip address -> it may be a problem if your router blocks that, solutions vary from adding your domain name mapped to the local ip, or just first visiting the local ip addres via https so it gets remembered and later resolved
- Change the domain name to resolve to your static ip -> https://my.eurodns.com/cloud/ssl#_ e.g. rumenplamenovart.com -> 213.91.236.77

# To build and run everything together
- To update the UI refer to the beforementioned UI repository. In this repository the release version of the angular_frontend_application image needs to be bumped (i.e. image: 'rocazzar/rumen-plamenov-angular-app:v1.0-release').  
- If any new packages were added execute "pip3 freeze > requirements.txt"
- docker compose build  -> to build the environments, volumes and images
- docker compose up -d
