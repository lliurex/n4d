
def startup_on_demand(self,auth, filter_variable_name, filter_variable_value):

	ret=self.builtin_validation(auth)
	
	if ret["status"]==0:	
		#internal core funciton
		self.startup_on_demand(True,filter_variable_name,filter_variable_value)
		return  n4d.responses.build_successful_call_response(True)

	else:
		return ret

#def set_variable

