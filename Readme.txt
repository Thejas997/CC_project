CC_1131_1621_1634 contains code for users vm
CC_1131_1621_1634 contains code for rides vm
zookeper_ampq contains code for Dbass application
open terminal inside every folder and do 
sudo docker stop $(sudo docker ps -aq)
sudo docker rm $(sudo docker ps -aq)
sudo docker-compose up --build --force recreate
To run start ride share application and insert correct urls for Dbass endpoints in rides and users apis as documented in code