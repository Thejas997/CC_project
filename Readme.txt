UE17CS352 CC Project
Team Members
PES1201701634 P Sudhamshu Rao
PES1201701621 S Thejas
PES1201701131 Vaibhav V Pawar
Our project aims to build a Ride share application using Docker, flask,zookeeper rabbitmq,and other programs. The Rides Share application contains many rest api endpoints using which our application can be accessed. For database we use sqlite3.All the flask applications are dockerised.We hosted all our application on AWS.There are three aws instances for users, rides, and database. This project mainly focuses on database. The database component contains three main part, Orchestrator which receives all incoming requests and directs it to appropriate endpoints, slave which serves reads the database, master which writes to the database.The orchestrator slave and master communicate using Rabbitmq.Zookeper is used for fault tolerance. If a slave fails a new slave is brought up, if a master fails a new master is elected. And orchestrator also brings up new 
CC_1131_1621_1634_users contains code for users vm
CC_1131_1621_1634_rides contains code for rides vm
zookeper_ampq contains code for Dbass application
open terminal inside every folder and do 
sudo docker stop $(sudo docker ps -aq)
sudo docker rm $(sudo docker ps -aq)
sudo docker-compose up --build --force-recreate
To run start ride share application and insert correct urls for Dbass endpoints in rides and users apis as documented in code
