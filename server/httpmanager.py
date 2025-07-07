import os
import os.path

import n4d.server.core


class HttpManager:
	
	ENABLED=True
	LISTING_ENABLED=True
	DEBUG=True
	
	SECTION_NOT_FOUND_ERROR=-1
	
	def __init__(self):
		
		self.core=n4d.server.core.Core.get_core()
		self.read_variable()
		
	#def init
	
	def dprint(self,data):
		
		self.core.pprint("HttpManager","%s"%str(data))
		
	#def dprint
	
	def read_variable(self):
		
		self.downloads={}
		
		ret=self.core.variables_manager.get_variable("HTTPMANAGER_DOWNLOADS")
		if ret["status"]==0:
			self.downloads=ret["return"]
		
	#def read_variable
	
	def add_download(self,section,file_path):

		if section not in self.downloads:
			self.downloads[section]=[]
		
		if file_path not in self.downloads[section]:
			self.downloads[section].append(file_path)
		
		self.save_variable()
		
		return n4d.responses.build_successful_call_response()
		
	#def add_download
	
	def save_variable(self):
		
		self.core.set_variable("HTTPMANAGER_DOWNLOADS",self.downloads)
		return True
		
	#def save_variable
	
	def get_download_list(self,section=None):
		
		ret=None
		
		if section==None:
			ret=self.downloads
		else:
			if section not in self.downloads:
				n4d.responses.build_failed_call_response(HttpManager.SECTION_NOT_FOUND_ERROR,"Section not found")
			else:
				ret=self.downloads[section]
		
		return n4d.responses.build_successful_call_response(ret)
		
	#def get_download_list
	
	def delete_download(self,section,file_path,delete_file=False):
	
		if section in self.downloads:
			if file_path in self.downloads[section]:
				self.downloads[section].remove(file_path)
				self.save_variable()
				if delete_file:
					if os.path.exists(file_path):
						os.remove(file_path)
				
		return n4d.responses.build_successful_call_response()
	
	#def delete_download

	
#class HttpManager