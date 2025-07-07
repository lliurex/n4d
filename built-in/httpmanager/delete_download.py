
def delete_download(self,auth,section,file_path,delete_file=False):

	allowed_groups=["sudo","admins","teachers"]

	ret=self.builtin_validation(auth,allowed_groups)
	
	if ret["status"]==0:	
		return self.core.http_manager.delete_download(section,file_path,delete_file)
	else:
		return ret

#def delete_download

