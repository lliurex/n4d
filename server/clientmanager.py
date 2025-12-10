import n4d.responses
import xmlrpc.client
import ssl
import threading
import time
import socket
import os
import json

import n4d.server.core

class ClientManager:
	
	REGISTER_SLEEP_TIME=60*3
	CHECK_CLIENTS_SLEEP_TIME=60*3
	MAX_MISSED_PINGS=3
	RUN_DIR="/run/n4d/clients/"
	CLIENTS_FILE=RUN_DIR+"clients.json"
	MACHINE_FILE="/etc/machine-id"
	
	def __init__(self):
		
		self.clients={}
		self.core=n4d.server.core.Core.get_core()
		self.server_id=None
		self.registering=False
		self.saving_lock=threading.Lock()
		if not os.path.exists(ClientManager.RUN_DIR):
			os.makedirs(ClientManager.RUN_DIR)
		self.load_clients_file()
		self.start_register_to_server_thread()
		self.start_check_clients_thread()
		
	#def __init__
	
	def startup(self,options):

		self.start_check_clients_thread()
		
	#def startup
	
	def dprint(self,data):
		self.core.pprint("ClientManager","%s"%str(data))
	#def dprint
	
	def start_register_to_server_thread(self):
		
		self.register_thread=threading.Thread(target=self.register_to_server,name="N4d.ClientManager.start_register_to_server_thread")
		self.register_thread.daemon=True
		self.register_thread.start()
		
	#def start_register
	
	def get_machine_id(self):
		
		machine_id=None
		try:
			f=open(ClientManager.MACHINE_FILE)
			machine_id=f.readline().strip("\n")
			f.close()
		except:
			pass
		
		return  n4d.responses.build_successful_call_response(machine_id)
		
	#def get_machine_id

	def register_to_server_on_demand(self):

		while self.registering:
			time.sleep(1)

		try:
			self.registering=True
			ret=self.core.variables_manager.get_variable("REMOTE_VARIABLES_SERVER")
			if ret["status"]==0:
				remote_server=ret["return"]
				if remote_server==None:
					return
				server_ip=socket.gethostbyname(remote_server)
				if server_ip not in self.core.get_all_ips():
					
					context=ssl._create_unverified_context()
					socket.setdefaulttimeout(5)
					c = xmlrpc.client.ServerProxy('https://%s:9779'%server_ip,context=context,allow_none=True)
					mac=self.core.get_mac_from_device(self.core.route_get_ip(server_ip))
					machine_id=self.get_machine_id()["return"]
					if machine_id!=None:
						ret=c.register_client("",mac,machine_id)
						if ret["status"]==0:
							self.server_id=ret["return"]
			
		except Exception as e:
			self.dprint(e)
			self.server_id=None
		
		socket.settimeout(None)
		self.registering=False
		return n4d.responses.build_successful_call_response(self.server_id)
		
	#def register_to_server_on_demand
	
	def register_to_server(self):
		
		while True:
			self.register_to_server_on_demand()
			time.sleep(ClientManager.REGISTER_SLEEP_TIME)

	#def register_n4d_instance_to_server
	
	def register_client(self,protected_ip,mac,machine_id):
		
		client={}
		client["last_check"]=int(time.time())
		client["missed_pings"]=0
		client["ip"]=protected_ip
		client["mac"]=mac
				
		self.clients[machine_id]=client
		self.save_clients_file()
		#self.dprint("Client [%s] %s - %s registered"%(machine_id,mac,protected_ip))
		
		return n4d.responses.build_successful_call_response(self.core.id,"Client added")
		
	#def register_instance
	
	def save_clients_file(self):
		
		self.saving_lock.acquire()
		
		f=open(ClientManager.CLIENTS_FILE,"w")
		data=json.dumps(self.clients,indent=4,ensure_ascii=False)
		f.write(data)
		f.close()
		
		self.saving_lock.release()
		
		return True

	#def save_clients
	
	def load_clients_file(self):
	
		if os.path.exists(ClientManager.CLIENTS_FILE):
			try:
				#self.dprint("Loading previous client file...")
				f=open(ClientManager.CLIENTS_FILE)	
				data=json.load(f)
				f.close()
				self.clients=data
			except Expcetion as e:
				self.dprint(e)
		
	#def load_clients_file
	
	def get_client_list(self,force_check=False):
		
		if force_check:
			self.check_clients(True)
		return n4d.responses.build_successful_call_response(self.clients)
		
	#def get_client_list
	
	def check_clients(self,wait_for_result=False):
		
		if not wait_for_result:
			clients_keys=list(self.clients)
			for machine_id in clients_keys:
				t=threading.Thread(target=self.check_client,args=(machine_id,),name="N4d.ClientManager.check_clients thread")
				t.daemon=True
				t.start()
			return n4d.responses.build_successful_call_response(self.clients,"check_clients thread launched. Current variable is probably not up to date")
		else:
			clients_keys=list(self.clients)
			for machine_id in clients_keys:
				self.check_client(machine_id)
			return n4d.responses.build_successful_call_response(self.clients)
		
	#def check_clients
	
	def check_client(self,machine_id):
		
		client=None
		
		if machine_id in self.clients:
			
			ip=self.clients[machine_id]["ip"]
			context=ssl._create_unverified_context()
			if machine_id not in self.clients:
				return n4d.responses.build_failed_call_response(machine_id,"Machine ID not ound")
			self.clients[machine_id]["last_check"]=int(time.time())
			try:
				c = xmlrpc.client.ServerProxy('https://%s:9779'%ip,context=context,allow_none=True)
				# Backup plan
				c.get_methods()
				self.clients[machine_id]["missed_pings"]=0
				# client responds. lets try to check machine_id
				try:
					ret=c.get_machine_id()
					client_machine_id=ret["return"]
					if client_machine_id == None:
						pass
					elif machine_id != client_machine_id:
						# looks like machine_id/ip combo has changed.
						if machine_id in self.clients:
							self.saving_lock.acquire()
							self.clients[client_machine_id]=self.clients[machine_id].copy()
							self.clients.pop(machine_id)
							self.saving_lock.release()
							self.save_clients_file()
							machine_id=client_machine_id
				except Exception as e:
					if machine_id in self.clients:
						self.clients[machine_id]["missed_pings"]+=1
				
			except:
				if machine_id in self.clients:
					self.clients[machine_id]["missed_pings"]+=1
			
			if machine_id in self.clients:
				if self.clients[machine_id]["missed_pings"]>=3:
					self.saving_lock.acquire()
					if machine_id in self.clients:
						client=self.clients.pop(machine_id)
					self.saving_lock.release()
					self.save_clients_file()
					return n4d.responses.build_failed_call_response(client,"Client has been dropped")
			
		
		if machine_id in self.clients:
			client=self.clients[machine_id]
			return n4d.responses.build_successful_call_response(client)
		else:
			return n4d.responses.build_failed_call_response(None,"Client has been dropped")
			
	#def check_client
	
	def start_check_clients_thread(self):
		
		t=threading.Thread(target=self.check_clients_thread)
		t.daemon=True
		t.start()
		
	#def start_check_clients_thread
	
	def check_clients_thread(self):
		
		while True:
			self.check_clients()
			time.sleep(ClientManager.CHECK_CLIENTS_SLEEP_TIME)
			#print(self.clients)
			
	#def check_clients_thread
	
