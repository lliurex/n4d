
def execute_oneshots(self,auth):

	ret=self.builtin_validation(auth)
	
	if ret["status"]==0:	
		#internal core funciton
		return self.execute_oneshots()
	else:
		return ret

#def set_variable

