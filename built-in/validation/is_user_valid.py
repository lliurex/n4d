def is_user_valid(self,user,password,group_list=None):
	
	#internal core function
	ret=self.validate_auth((user,password))
	
	if not group_list:
		group_list=[]
	
	if ret["status"]==0:
		
		if type(group_list)==list and len(group_list)>0:
			user_group_list=ret["return"][1]
			for group in user_group_list:
				if group in group_list:
					return n4d.responses.build_successful_call_response(True)
			return n4d.responses.build_successful_call_response(False,"User doesn't belong to requested group list")
		else:
			return n4d.responses.build_successful_call_response(True)
	
	return n4d.responses.build_successful_call_response(False,"User and/or password error")

#def is_user_valid
