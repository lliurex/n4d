import os
import os.path

import n4d.server.core


class HttpManager:
	
	ENABLED=True
	LISTING_ENABLED=True
	DEBUG=True
	
	SECTION_NOT_FOUND_ERROR=-1
	FILE_NOT_FOUND_ERROR=-10
	FILE_ALREADY_EXISTS_ERROR=-20
	
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
			if os.path.exists(file_path):
				if file_path not in self.downloads[section]:
					self.downloads[section].append(file_path)
				else:
					return n4d.responses.build_failed_call_response(HttpManager.FILE_ALREADY_EXISTS_ERROR,"File was previously added.")
			else:
				return n4d.responses.build_failed_call_response(HttpManager.FILE_NOT_FOUND_ERROR,"File not found")
		
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
				return n4d.responses.build_failed_call_response(HttpManager.SECTION_NOT_FOUND_ERROR,"Section not found")
			else:
				ret=self.downloads[section]
		
		return n4d.responses.build_successful_call_response(ret)
		
	#def get_download_list
	
	def get_download_urls(self, section):
		
		if section==None or section not in self.downloads:
			return n4d.responses.build_failed_call_response(HttpManager.SECTION_NOT_FOUND_ERROR,"Section not found")
		
		download_list=[]
		
		for download in self.downloads[section]:
			file_name=download.split("/")[-1]
			url="https://%s:9779/"+"%s/%s"%(section,file_name)
			download_list.append(url)
			
		return n4d.responses.build_successful_call_response(download_list)
		
		
	#def get_download_urls
	
	def delete_download(self,section,file_path,delete_file=False):
	
		if section in self.downloads:
			if file_path in self.downloads[section]:
				self.downloads[section].remove(file_path)
				self.save_variable()
				if delete_file:
					if os.path.exists(file_path):
						os.remove(file_path)
				n4d.responses.build_successful_call_response()
			
		
		return n4d.responses.build_failed_call_response(HttpManager.FILE_NOT_FOUND_ERROR,"File not found")
	
	#def delete_download

	
#class HttpManager