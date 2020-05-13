import logging
import math
import docker
from kazoo.client import KazooClient
from kazoo.client import KazooState
import time
import os
import pika
import uuid
import json
from flask import Flask, render_template,jsonify,request,abort
from multiprocessing import Value
import threading

time.sleep(20)
pid = os.getpid()
pid=str(pid)
app=Flask(__name__)

number_of_read_requests = Value('i', 0)

#write queue rpc
class writeMessage(object):
	def __init__(self):
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host='rmq',heartbeat=500,socket_timeout=None))

		self.channel = self.connection.channel()

		result = self.channel.queue_declare(queue='', exclusive=True)
		self.callback_queue = result.method.queue

		self.channel.basic_consume(
			queue=self.callback_queue,
			on_message_callback=self.on_response,
			auto_ack=True)

	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body

	def call(self, message_content):
		self.response = None
		self.corr_id = str(uuid.uuid4())
		self.channel.basic_publish(
			exchange='',
			routing_key='write_queue',
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.corr_id,
			),
			body=message_content)
		print("sent\n")
		while self.response is None:
		   self.connection.process_data_events()
		print(self.response)
		return self.response
		#return int(self.response)
		#print("for the request : ","\n the result is > ",self.response)

#read queue rpc
class readMessage(object):
	def __init__(self):
		self.connection = pika.BlockingConnection(
			pika.ConnectionParameters(host='rmq',heartbeat=500,socket_timeout=None))

		self.channel = self.connection.channel()

		result = self.channel.queue_declare(queue='', exclusive=True)
		self.callback_queue = result.method.queue

		self.channel.basic_consume(
			queue=self.callback_queue,
			on_message_callback=self.on_response,
			auto_ack=True)

	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body

	def call(self, message_content):
		self.response = None
		self.corr_id = str(uuid.uuid4())
		self.channel.basic_publish(
			exchange='',
			routing_key='read_queue',
			properties=pika.BasicProperties(
				reply_to=self.callback_queue,
				correlation_id=self.corr_id,
			),
			body=message_content)
		
		while self.response is None:
			self.connection.process_data_events()
		
		return self.response
		#return json.loads(self.response)



def create_new_worker():
	
	global worker_id,pid
	
	#docker sdk
	client = docker.from_env()

	print ("CREATING NEW CONTAINER >>>")
	client.images.build(path=".",tag="master")
	client.images.build(path=".",tag="slave")
	#p=client.containers.create("master",detach="True")
	#,name="worker"+str(worker_id)
	worker_id+=1	
	if(worker_id==0):
		q=client.containers.run("master",command="python worker.py",network='zookeeper_amqp_default',links={'rmq':'rmq','zoo':'zoo'},pid_mode="host",auto_remove=False,detach="True",name="master")
		print("Master container created")
	else:
		
		slave_name = str(worker_id) + "_slave_" + str(pid)
		client.containers.run("slave",command="python worker.py",links={'rmq':'rmq','zoo':'zoo'},network="zookeeper_amqp_default",detach=True,pid_mode="host",name=slave_name)
		os.system("docker cp master:code/database.db data.db")
		os.system("docker cp data.db "+slave_name+":code/database.db")	
		print("Slave container : ",slave_name," created");

logging.basicConfig()

zk = KazooClient(hosts='zoo:2181')
zk.start()
#zk.delete("/workers", recursive=True)
zk.ensure_path("/workers")
worker_id = -1
number_of_active_requests = 0
total_number_of_workers = 3


@zk.ChildrenWatch("/workers")
def watch_children(children):
	children = zk.get_children("/workers")
	print("There are %s children with names %s" % (len(children), children))
	
	
	for z_single_node in children:
		z_data,stat = zk.get("/workers/"+str(z_single_node))
		print("%s >>> %s" % (z_single_node,z_data))

	#if(len(children) < total_number_of_workers):
	#	create_new_worker()
		
	#time.sleep(3)

def crash_slave():
	client = docker.from_env()
	
	#print("CRASH API")
	pid_dict = dict()
	
	try:
		#print("CONTAIN LIST",client.containers.list)
		for container in client.containers.list():
			if "slave" in container.name:
				pid_dict[container.top()['Processes'][0][2]] = container
		print("DICT OF WORKERS :: ",pid_dict)
		min_pid = min(pid_dict.keys())
		container = pid_dict[min_pid]
		container.stop()
		client.containers.prune()
		print("\nSLAVE CONTAINER CRASHED ",min_pid,"\n")
		return str(min_pid)

	except:
		return '0'
		#print("\nNO SLAVE CONTAINERS\n")

"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
USE THESE FUNCTIONS FOR TESTING READ WRITE
read_req
write_req
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""
def read_req():
	global read_queue
	
	""" INPUT REQUEST """	
	a={'action':'select','table':'user_ride','columns':'*','where':'NA'}

	result = read_queue_inst.call(json.dumps(a))
	print('The read request : ',a,"\nThe read result>>> ",result)



def write_req():
	global write_queue
	
	a={}
	result = write_queue_inst.call(json.dumps(a))
	print('The write request : ',a,"\nThe write result>>> ",result)





print("ORCH IS RUNNING ...")


connection = pika.BlockingConnection(
	pika.ConnectionParameters(host='rmq'))
channel = connection.channel()

#sync exchange
channel.exchange_declare(exchange='syncing', exchange_type='fanout')

#read and write rpc instance
read_queue_inst = readMessage()
write_queue_inst = writeMessage()

	
'''
if __name__ == '__main__':
	createMaster()
	createSlave()
	createSlave()
	
	app.debug=True
	app.run('0.0.0.0',use_reloader=False)
'''
#ii=1
'''
create_new_worker()
time.sleep(2)
create_new_worker()
time.sleep(2)
create_new_worker()
'''

#scaling

def scale():
	global total_number_of_workers,zk,number_of_read_requests
	
	current_read_request = number_of_read_requests.value 
	
	with number_of_read_requests.get_lock():
		number_of_read_requests.value = 0
	
	#print("CURRENT : ",total_number_of_workers,"\nREQUIRED",current_read_request // 20)
	re_w = int(math.ceil(current_read_request/20))
	total_number_of_workers = max(re_w,1)
	
	children = zk.get_children("/workers")
	
	if((len(children)-1) < total_number_of_workers):
		for j in range(total_number_of_workers-len(children)+1):
			try:
				create_new_worker()
				time.sleep(3)
			except:
				pass
	else:
		for j in range(len(children)-1 - total_number_of_workers):
			crash_slave()
			#total_number_of_workers-=1
			time.sleep(3)
				
def scaling_wrapper():
	global number_of_read_requests
	
	while 1:
		time.sleep(120)
		print("ADJUSTING WORKER NODES")
		
		scale()



#FLASK API'S

@app.route('/api/v1/db/write',methods=["POST"])
def write_database():
	global write_queue_inst
	
	data = request.get_json()
	json_message = json.dumps(data)
	
	response = write_queue_inst.call(json_message)
	
	#print(" [.] Got %r" % response)
	response=str(response)
	if(response.find("in")!=-1):
		return str(response[0]),200
	else:
		return str(response[0]),201

@app.route('/api/v1/db/read',methods=["POST"])
def read_database():
		global read_queue_inst
		
		with number_of_read_requests.get_lock():
			number_of_read_requests.value += 1
		data = request.get_json()
		print(data)
		json_message = json.dumps(data)
		print(json_message)
		print(json_message)
		#print(" [x] client started reading...")
		result = read_queue_inst.call(json_message)
		
		#print(" [.] client Got ... %r" % result)
		
		return result,200
@app.route('/api/v1/db/clear',methods=["POST"])
def clear_database():
	global write_queue_inst
	
	data = {'action':'d','columns':'d','table':'d','where':'d','values':'d'}
	json_message = json.dumps(data)
	print("in")
	write_queue_inst.call(json_message)
	return 'success',200

@app.route("/api/v1/crash/master",methods=["POST"])
def crash_master():
	return {},200

@app.route("/api/v1/worker/list",methods=["GET"])
def woker_list():
	global zk
	l=[]
	l=zk.get_children("/workers")
	l.sort()
	return json.dumps(l),200

@app.route("/api/v1/crash/slave",methods=["POST"])
def crash_slave_inp():
	result = crash_slave()
	return result,200

'''
@app.route('/api/v1/_count',methods=["GET"])
def get_count_requests():
	l=[]
	l.append(number_of_read_requests.value)
	return jsonify(l), 200


@app.route('/api/v1/_count',methods=["DELETE"])
def delete_count_requests():
	global number_of_read_requests
	with number_of_read_requests.get_lock():
		number_of_read_requests.value = 0
	return {},200
'''	

'''
while 1:
	#	global worker_id
	#print(i)
	#print("WORKER ID",worker_id)
	if((worker_id >= 2) and (i%500==0)):
		#read_req()
		#crash_slave();
	i+=1
'''
if __name__ == '__main__':
	create_new_worker()
	time.sleep(3)
	create_new_worker()
	time.sleep(3)
	
	scaling_inst = threading.Thread(target=scaling_wrapper)
	scaling_inst.start()

	
	app.debug=True
	app.run('0.0.0.0',use_reloader=False)

