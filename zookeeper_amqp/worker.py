import logging
from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.recipe.watchers import DataWatch,ChildrenWatch
import time
import pika
import time
import os
import json
from flask import jsonify
import sqlite3 as sq3
def delete_data():
	global db_connection,db_cursor
	
	db_cursor.execute("DELETE FROM users")
	db_cursor.execute("DELETE FROM user_ride")
	db_connection.commit()
def write_to_db(write_json):
	global db_connection,db_cursor
	
	channel.basic_publish(exchange='syncing', routing_key='', body=write_json)
	#convert string json to dict
	temp_dict = eval(write_json)

	action=temp_dict['action']
	scolumn=temp_dict['columns']
	table=temp_dict['table']
	where=temp_dict['where']
	values=temp_dict['values']
		
	values.strip(",")
	values=values.split(",")
	
	try:
		db_cursor.execute("CREATE TABLE users (username varchar,password varchar)")
		db_cursor.execute('CREATE TABLE user_ride(ride INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,timestamp TEXT,source TEXT,destination TEXT,ride_mate TEXT)')

		db_connection.commit()
	except:
		yr=0
	if(action=='d'):
		print("o")
		delete_data()
	
		return "in"
	if(action == "delete"):
		
		where=where.split(";")

		
		
		
		existing_usersdb=db_cursor.execute("DELETE FROM  "+table+" WHERE "+where[0] +"=(?)",(where[1],))
		
		db_connection.commit()
		return "in"
		
	if(action == "update"):
		where=where.split(";")
		return "in"
		existing_usersdb=db_cursor.execute("UPDATE "+table+" SET "+scolumn+"="+"\'"+values[0]+"\'"+" WHERE "+where[0] +"=(?)",(where[1],))

		db_connection.commit()
		return "uodate success"
	if(action == "insert" and table=="user_ride"):
		
		existing_usersdb=db_cursor.execute("INSERT INTO"+"\'"+table +"\'"+"(username,timestamp,source,destination) "+"VALUES(?,?,?,?)",(values[0],values[1],values[2],values[3]))
		
		db_connection.commit()
		return "success"
		
	if(action == "insert" and table=="users"):
		existing_usersdb=db_cursor.execute("INSERT INTO"+"\'"+table+"\'"+"VALUES(?,?)",(values[0],values[1]))
		db_connection.commit()
		return "success"


def sync_write(write_json):
	#write json is dict 
	global db_connection,db_cursor,is_master
	
	print("SYNC RECEIVES ",write_json,type(write_json))
	
	temp_dict = write_json

	action=temp_dict['action']
	scolumn=temp_dict['columns']
	table=temp_dict['table']
	where=temp_dict['where']
	values=temp_dict['values']
		
	values.strip(",")
	values=values.split(",")
	
	try:
		db_cursor.execute("CREATE TABLE users (username varchar,password varchar)")
		db_cursor.execute('CREATE TABLE user_ride(ride INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,timestamp TEXT,source TEXT,destination TEXT,ride_mate TEXT)')
		db_connection.commit()
	except:
		yr=0
	if(action=='d'):
		delete_data()
	if(action == "delete"):
		
		where=where.split(";")

		
		
		
		existing_usersdb=db_cursor.execute("DELETE FROM  "+table+" WHERE "+where[0] +"=(?)",(where[1],))
		
		db_connection.commit()
		#return "succesfull",201
	if(action == "update"):
		where=where.split(";")
		
		existing_usersdb=db_cursor.execute("UPDATE "+table+" SET "+scolumn+"="+"\'"+values[0]+"\'"+" WHERE "+where[0] +"=(?)",(where[1],))
		db_connection.commit()
		#return "uodate success"
	if(action == "insert" and table=="user_ride"):
		
		existing_usersdb=db_cursor.execute("INSERT INTO"+"\'"+table +"\'"+"(username,timestamp,source,destination) "+"VALUES(?,?,?,?)",(values[0],values[1],values[2],values[3]))
		
		db_connection.commit()
		#return "success"
		
	if(action == "insert" and table=="users"):
		existing_usersdb=db_cursor.execute("INSERT INTO"+"\'"+table+"\'"+"VALUES(?,?)",(values[0],values[1]))
		db_connection.commit()
		#return "success"



def read_from_db(read_json):
	global db_connection,db_cursor
	print("read json> ",read_json)
	#convert json to dict
	
	temp_dict = eval(read_json.decode())

	action=temp_dict['action']
	table=temp_dict['table']
	columns=temp_dict['columns']
	where=temp_dict['where']
	
	if(action == "select" and where == "NA"):
		try:
			existing_usersdb=db_cursor.execute("SELECT"+ columns+"FROM" +"\'"+table+"\'")
			y=existing_usersdb.fetchall()
			r=""
			if(table=="user_ride"):
				for i in y:
					r=r+"+"+str(i)
			else:
				for i in y:
					r=r+","+str(i[0])

			if(r==""):
				return "NA"
			return r
		except:
			db_cursor.execute("CREATE TABLE users (username varchar,password varchar)")
			db_connection.commit()
			existing_usersdb=db_cursor.execute("SELECT"+ columns+"FROM" +"\'"+table+"\'")
			y=existing_usersdb.fetchall()
			r=""
			if(table=="user_ride"):
				for i in y:
					r=r+"+"+str(i)
			else:
				for i in y:
					r=r+","+str(i[0])

			if(r==""):
				return "NA"
			return r

	elif( where !="NA"):
		where=where.split(";")
		
		if(len(where) == 4):
			
			existing_usersdb=db_cursor.execute("SELECT "+ columns+" FROM" +"\'"+table+"\'"+"WHERE "+where[0]+" = " +"\'"+where[1]+"\'"+" and "+where[2]+" = " +"\'"+where[3]+"\'")
			y=existing_usersdb.fetchall()
			
			r=""
			u=""
			for i in y:
				r=r+"+"+str(i)
		else:
			

		
			existing_usersdb=db_cursor.execute("SELECT "+ columns+" FROM " +table+" WHERE "+where[0]+"=(?)",(where[1],))
			y=existing_usersdb.fetchall()
			r=""
			u=""
			for i in y:
				u=i
				if(u == ""):
					return ""
				for i in u:
					r=r+","+str(i)

		
		if(r==""):
			return "NA"
		return r



	

def serve_write_request(ch, method, props, body):
	
	#body : json in string bytes format
	response = write_to_db(body.decode())
	print(response)
	#print("WRITE REQUEST IS ",body,type(body))
	
	ch.basic_publish(exchange='',
					 routing_key=props.reply_to,
					 properties=pika.BasicProperties(correlation_id = \
														 props.correlation_id),
					 body=response)
	ch.basic_ack(delivery_tag=method.delivery_tag)
	

'''	
def on_read_request(ch, method, props, body):
	print("request for read >>> ",body)
	json_msg = json.loads(body)
	response = json_msg
	print("read request result is > ",response)
	#response = {"key" : "value"}
	ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                        props.correlation_id),
                     body=json.dumps(response))
	ch.basic_ack(delivery_tag=method.delivery_tag)
'''
#body = json.dumps(response)

def serve_read_request(ch,method, props, body):
	
	
	
	
	#body contains json read request
	response = read_from_db(body)
	#receive json object, currently receiving string
	
	ch.basic_publish(exchange='',
					 routing_key=props.reply_to,
					 properties=pika.BasicProperties(correlation_id = \
														 props.correlation_id),
					 body=response)
	ch.basic_ack(delivery_tag=method.delivery_tag)

pid = os.getppid()
pid=str(pid)
print("PID OF WORKER >> ",pid)
is_master = False


#zookeeper
logging.basicConfig()

zk = KazooClient(hosts='zoo:2181')
zk.start()

zk.ensure_path("/workers")
zk.create(path="/workers/"+str(pid),value=pid.encode(),ephemeral=True)

#database connection
#,check_same_thread=False
db_connection = sq3.connect('database.db')
db_cursor = db_connection.cursor()


#rabbitmq connection
connection = pika.BlockingConnection(
	pika.ConnectionParameters(host='rmq',heartbeat=500,socket_timeout=None))
channel = connection.channel()

#queue for read write rpc
channel.queue_declare(queue='write_queue')
channel.queue_declare(queue='read_queue')


#sync queue's exchange
channel.exchange_declare(exchange='syncing', exchange_type='fanout')


time.sleep(5)
children = zk.get_children("/workers")
children.sort()
if(children[0]==pid):
	is_master = True



channel.basic_qos(prefetch_count=1)


if(is_master):
	
	print("waiting for write requests")
	channel.basic_consume(queue='write_queue', on_message_callback=serve_write_request)
	
else:
	print("waiting for read requests")
	channel.basic_consume(queue='read_queue', on_message_callback=serve_read_request)
	
	#one sync queue for each normal worker
	sync_queue = str(pid) + "sync_queue"
	channel.queue_declare(queue=sync_queue, exclusive=False)
	channel.queue_bind(exchange='syncing', queue=sync_queue)
	print('reading sync queue')
	
	def callback_sync(ch, method, properties, body):
		body = json.loads(body)
		sync_write(body)

	channel.basic_consume(queue=sync_queue, on_message_callback=callback_sync, auto_ack=True)

#both for master and normal worker	
channel.start_consuming()
while 1:
	time.sleep(3)
	print('1')


