
def add_download(self,auth,section,file_path):

	allowed_groups=["sudo","admins","teachers"]

	ret=self.builtin_validation(auth,allowed_groups)
	
	if ret["status"]==0:	
		return self.http_manager.add_download(section,file_path)
	else:
		return ret

#def add_download

