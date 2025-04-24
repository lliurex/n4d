# -*- coding: utf-8 -*-
import PAM
import multiprocessing

class PamManager:
	
	def __init__(self,module="common-auth"):
		self.user = None
		self.passwd = None
		self.auth = PAM.pam()
		self.auth.start(module)
	
	def authentication(self,user,passwd):
		
		def pam_conv(auth, query_list, userData):
			resp = []
			for i in range(len(query_list)):
				query, type = query_list[i]
				if type == PAM.PAM_PROMPT_ECHO_ON :
					resp.append((user),0)
				if type == PAM.PAM_PROMPT_ECHO_OFF:
					resp.append((passwd, 0))
				elif type == PAM.PAM_ERROR_MSG or type == PAM.PAM_TEXT_INFO:
					resp.append(('', 0))
				else:
					return None
			return resp
			
		def validate(ret_queue):
			try:
				self.auth.authenticate()
				self.auth.acct_mgmt()
				ret_queue.put(True)
			except Exception as e:
				ret_queue.put(False)
			
		
		self.auth.set_item(PAM.PAM_USER, user)
		self.auth.set_item(PAM.PAM_CONV,pam_conv)
		
		ret=multiprocessing.Queue()
		p=multiprocessing.Process(target=validate,args=(ret,))
		p.start()
		p.join()
		return(ret.get())
		