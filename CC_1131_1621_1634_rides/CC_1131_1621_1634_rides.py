from flask import Flask, render_template,\
jsonify,request,abort
import re
import sqlite3 as sq3
import datetime
import requests
import flask
from datetime import datetime

app=Flask(__name__)
global domain
global load_addr
domain = "CC-897869852.us-east-1.elb.amazonaws.com"#note: please insert correct url for DBAAS service endpoint
load_addr = "CC-897869852.us-east-1.elb.amazonaws.com"#note: please insert correct url for DBAAS service endpoint



f=open("file.txt","w")

f.close()

@app.errorhandler(404)

def g(e):

	

	return "error 404 page not found",404

@app.errorhandler(405)

def g1(e):

	f=open("file.txt","a")

	f.write('a')

	f.close()

	return "Method not allowed",405



	
@app.route('/api/v1/rides',methods=["POST"])
def new_ride():
	global domain
	global load_addr
	f=open("file.txt","a")

	f.write('a')

	f.close()
	username=request.get_json()["created_by"]
	timestamp=request.get_json()["timestamp"]
	source=request.get_json()["source"]
	destination=request.get_json()["destination"]
	userdb_connection=sq3.connect('user_details.db')
	cursor_user=userdb_connection.cursor()
	f = open("AreaNameEnum.csv", "r")
	Lines = f.readlines() 
	for i in Lines:
		p=i.replace("\"","")
		p=p.split(",")
		if(str(source) == p[0]):
			source=p[1].strip("\n")
		if(str(destination) == p[0]):
			destination=p[1].strip("\n")


	
	url= 'http://'+load_addr+':80/api/v1/users'
	headers={"Origin":domain}
	p=requests.get(url,headers=headers)
	if(not(p.text == "empty")):
		existing_users = p.json()
	else:
		abort(400)
	
	if(username in existing_users):
		
		values=username+","+timestamp+","+source+","+destination
		post={"action":"insert","table":"user_ride","columns":"NA","where":"NA","values":values}
		url= 'http://'+domain+':80/api/v1/db/write'
		p=requests.post(url,json=post)
		t=p.text
		return "",201



	else:
		abort(400)
@app.route('/api/v1/rides/<rideId>',methods=["GET"])
def ride_details(rideId):
	global domain
	global load_addr
	f=open("file.txt","a")

	f.write('a')

	f.close()
	
	t="ride;"+rideId
	post={"action":"select","table":"user_ride","columns":"*","where":t}
	url= 'http://'+domain+':80/api/v1/db/read'
	p=requests.post(url,json=post)
	
	
	
	if(p.text == "NA"):
		return "",400
	u=p.text
	p=u.strip(",")
	p=p.split(",")
	
	
	

	rides={}
	values = ["rideId","created_by","timestamp","source","destination","users"]
	index = 0
	
	
		
	for j in p:
		if index == 5:
		
			if(j!="None"):
				
				riders=j.split(";")
				
				rides[values[5]]=riders
			else:
				rides[values[index]] = []
		else:
			rides[values[index]] = j
		index +=1
	if("users" not in rides):
		rides["users"]=[]
	return jsonify(rides),200
@app.route('/api/v1/rides/<rideId>',methods=["POST"])
def join_ride(rideId):
	global domain
	global load_addr
	f=open("file.txt","a")

	f.write('a')

	f.close()

	username_requesting=request.get_json()["username"]
	

	



	

	url= 'http://'+load_addr+':80/api/v1/users'
	headers={"Origin":domain}
	p=requests.get(url,headers=headers)
	if(not(p.text == "empty")):
		existing_users = p.json()
	else:
		abort(400)
	
	
	if(not username_requesting in existing_users):
		return "",400
	
	post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
	url= 'http://'+domain+':80/api/v1/db/read'
	headers={"Origin":domain}
	p=requests.post(url,json=post)
	if(p.text == "NA"):
		return "",400
	t=p.text
	r=1
	t=t.strip("+")
	t=t.split("+")
	for i in t:
		p=i.strip("()")
		p=p.split(",")
		if str(rideId) in p:
			r=0
			break
	
	

	
	if r:
		return "",400
	else:
		t="ride;"+rideId
		post={"action":"select","table":"user_ride","columns":"*","where":t}
		url= 'http://'+domain+':80/api/v1/db/read'
		headers={"Origin":domain}
		p=requests.post(url,json=post)
		u=p.text
		p=u.strip(",")
		p=p.split(",")
		if(p[1] == username_requesting):
			return "",400
		
		

	
	
	if(len(p) < 6):
		updated_ride_mates=username_requesting
	else:
		updated_ride_mates= username_requesting + ";"+p[5]
		if(p[5]=="None"):
			updated_ride_mates=username_requesting
		res = p[5].split(";")
		if(username_requesting in res):
			return "alraedy there",200
	
	

		
	
	
	
					
	t="ride;"+rideId
	post={"action":"update","table":"user_ride","columns":"ride_mate","where":t,"values":updated_ride_mates}
	url= 'http://'+domain+':80/api/v1/db/write'
	headers={"Origin":domain}
	p=requests.post(url,json=post)
	return p.text,200



@app.route('/api/v1/rides/<ridesId>',methods=["DELETE"])
def ride_delete(ridesId):
	global domain
	global load_addr
	f=open("file.txt","a")

	f.write('a')

	f.close()
	


	
	
	post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
	url= 'http://'+domain+':80/api/v1/db/read'
	headers={"Origin":domain}
	p=requests.post(url,json=post)
	if(p.text == "NA"):
		abort(400)
	t=p.text
	r=0
	t=t.strip("+")
	t=t.split("+")
	for i in t:
		p=i.strip("()")
		p=p.split(",")
		if str(ridesId) in p:
			r=1
			break
	
	

	
	if r:
		
		
		t="ride;"+ridesId

		post={"action":"delete","table":"user_ride","columns":"i","where":t,"values":"NA"}
		url= 'http://'+domain+':80/api/v1/db/write'
		headers={"Origin":domain}
		p=requests.post(url,json=post)
		t=p.text
		return p.text,200
		
	else:
		return "Ride Id does not exist",400

@app.route('/api/v1/rides',methods=["GET"])
def uprides():
	global domain
	global load_addr
	f=open("file.txt","a")

	f.write('a')

	f.close()
	args = request.args
	source=args["source"]
	destination=args["destination"]
	if(source == "" or destination == ""):
		abort(400)

	f = open("AreaNameEnum.csv", "r")
	Lines = f.readlines() 
	for i in Lines:
		p=i.replace("\"","")
		p=p.split(",")
		if(str(source) == p[0]):
			source=p[1].strip("\n")
		if(str(destination) == p[0]):
			destination=p[1].strip("\n")

	
     
	t="source;"+source+";"+"destination"+";"+destination
	if(source == "" or destination == ""):
		abort(400)

	post={"action":"select","table":"user_ride","columns":"*","where":t}
	url='http://'+domain+':80/api/v1/db/read'
	headers={"Origin":domain}
	p=requests.post(url,json=post)
	if(p.text == "NA"):
		return "",204
	y=[]
	
	urides={}
	t=p.text
	t=t.strip("+")
	t=t.split("+")
	
	
	for i in t:
		i=i.strip("()")
		i=i.replace("\'","")
		i=i.split(",")
		i[2]=i[2].strip(" ")
		i[1]=i[1].strip(" ")
	
		
		p=datetime.strptime(i[2],'%d-%m-%Y:%S-%M-%H')
		now =datetime.now()
		
	
		if(p > now):
			urides["rideId"]=i[0]
			urides["username"]=i[1]
			urides["timestamp"]=i[2]
			y.append(urides)
			urides={}

			
	if(len(y)==0):
		return "",204	
	return jsonify(y),200

@app.route('/api/v1/rides/count')
def ride_count():
	global domain
	global load_addr
	f=open("file.txt","a")

	f.write('a')

	f.close()
	post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
	url='http://'+domain+':80/api/v1/db/read'
	headers={"Origin":domain}
	p=requests.post(url,json=post)
	y=[]

	if(p.text == "NA"):
		y.append(0)
		return jsonify(y),200
	
	
	
	t=p.text
	t=t.strip("+")
	t=t.split("+")
	p=len(t)
	y.append(p)
	return jsonify(y),200
@app.route('/api/v1/_count',methods=["GET"])

def get_count():
	global domain
	global load_addr

       	
	f=open("file.txt","r")


	p=list()
	p.append(len(f.read()))

	return jsonify(p),200
	
@app.route('/api/v1/_count',methods=["DELETE"])
def del_count():
	global domain
	global load_addr

       	
	f=open("file.txt","w")
	f.close()
	return "done",200
	


if __name__ == '__main__':	
	app.debug=True
	app.run(host='0.0.0.0',port=80)
			

	
