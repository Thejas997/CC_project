from flask import Flask, render_template,\
jsonify,request,abort
import re
import sqlite3 as sq3
import datetime
import requests
import flask
from datetime import datetime

app=Flask(__name__)


f=open("file.txt","w")

f.close()
#the below two decorators are for counting error requests
@app.errorhandler(404)

def g(e):

	

	return "error 404 page not found",404

@app.errorhandler(405)

def g1(e):

	f=open("file.txt","a")

	f.write('a')

	f.close()

	return "Method not allowed",405



#URL Routing:
#the below function is for adding a new user

@app.route('/api/v1/users',methods=["PUT"])
def add_user():
	
	
	f=open("file.txt","a")

	f.write('a')

	f.close()
	username=request.get_json()["username"]
	password=request.get_json()["password"]
	post={"action":"select","table":"users","columns":"*","where":"NA"}
	url= 'http://CC-897869852.us-east-1.elb.amazonaws.com:80/api/v1/db/read'#note: please insert correct url for DBAAS service endpoint
	headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
	p=requests.post(url,json=post)
	if(p.text!="NA"):
		
		r=p.text
		
		r=r.strip(",")
		
		existing_users=r.split(",")
		for i in existing_users:
			if(i == username):
				
				return "",400
				break
	
	





	
	if(not re.search("^[a-fA-F0-9]{40}$",password)):

		
		abort(400)
	
	
	values=username+","+password
	post={"action":"insert","table":"users","columns":"*","where":"NA","values":values}
	url= 'http://CC-897869852.us-east-1.elb.amazonaws.com:80/api/v1/db/write'#note: please insert correct url for DBAAS service endpoint
	headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
	p=requests.post(url,json=post)
	t=p.text
	return "",201

	
		
	
@app.route('/api/v1/users/<user>',methods=["DELETE"])
def remove_user(user):
	
	
	f=open("file.txt","a")

	f.write('a')

	f.close()
	post={"action":"select","table":"users","columns":"*","where":"NA"}
	url= 'http://'+"CC-897869852.us-east-1.elb.amazonaws.com"+':80/api/v1/db/read'#note: please insert correct url for DBAAS service endpoint
	headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
	p=requests.post(url,json=post)
	
	if(p.text == "NA"):
		abort(400)
	r=p.text
	r=r.strip(",")
	
	
	existing_users=r.split(",")
	
	if(user in existing_users):
		t="username;"+user
	
		post={"action":"delete","table":"users","columns":"NA","where":t,"values":"NA"}
		url= 'http://'+"CC-897869852.us-east-1.elb.amazonaws.com"+':80/api/v1/db/write'#note: please insert correct url for DBAAS service endpoint
		headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
		p=requests.post(url,json=post)
		
		
		
		
		post={"action":"select","table":"user_ride","columns":"*","where":"NA"}
		url= 'http://'+"CC-897869852.us-east-1.elb.amazonaws.com"+':80/api/v1/db/read'#note: please insert correct url for DBAAS service endpoint
		headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
		p=requests.post(url,json=post,headers=headers)
		t=p.text
		

		
		if(p.text != "NA" ):
			t=p.text
			
			t=t.strip("+")
			t=t.split("+")
			f=0
			for i in t:
				
				i=i.strip("()")
				i=i.split(",")
				
				if(user in i[5]):
					t="ride;"+i[0]
					f=1
					
					p1=i[5].replace(user,"")
					p1=p1.replace("\'","")
					p1=p1.split(";")
					
					
					p2=""
					for j in p1:
						
						if(j!=" "):
							p2=p2+";"+j
					p2=p2.strip(";")
				
					post={"action":"update","table":"user_ride","columns":"ride_mate","where":t,"values":p2}
					url= 'http://'+"CC-897869852.us-east-1.elb.amazonaws.com"+':80/api/v1/db/write'#note: please insert correct url for DBAAS service endpoint
					headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
					p=requests.post(url,json=post,headers=headers)
					t=p.text
					
				i[1]=i[1].replace("\'","")
				i[1]=i[1].strip(" ")
				
				if(user in i):
					
					t="ride;"+i[0]
					
					post={"action":"delete","table":"user_ride","columns":"NA","where":t,"values":"NA"}
					url= 'http://'+"CC-897869852.us-east-1.elb.amazonaws.com"+':80/api/v1/db/write'#note: please insert correct url for DBAAS service endpoint
					headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
					p=requests.post(url,json=post,headers=headers)
					t=p.text
					
			return t+"succesfully deleted in user rides if any rides",200
		

			
			return "out",200
		else:
			return "empty",200
	else:
		abort(400)

@app.route('/api/v1/users',methods=["GET"])
def list_all_users():
	
	
	f=open("file.txt","a")
	f.write('a')
	f.close()
	post={"action":"select","table":"users","columns":"*","where":"NA"}
	url= 'http://CC-897869852.us-east-1.elb.amazonaws.com:80/api/v1/db/read'#note: please insert correct url for DBAAS service endpoint
	headers={"Origin":"CC-897869852.us-east-1.elb.amazonaws.com"}
	p=requests.post(url,json=post)
    

	l=list()
	if(p.text!="NA"):

		r=p.text

		r=r.strip(",")

		existing_users=r.split(",")
		for i in existing_users:
			l.append(i)
	else:
		return "empty",400
	return jsonify(l)
#below function is used for counting number of http_requests
@app.route('/api/v1/_count',methods=["GET"])

def get_count():
	
	

       	
	f=open("file.txt","r")


	p=list()
	p.append(len(f.read()))

	return jsonify(p),200

#below function is used for resetting count api
@app.route('/api/v1/_count',methods=["DELETE"])
def del_count():
	
	

       	
	f=open("file.txt","w")
	f.close()
	return "done",200

if __name__ == '__main__':	
	app.debug=True
	app.run(host='0.0.0.0',port=80)
        
