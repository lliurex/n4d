# -*- coding: utf-8 -*-
import PAM

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
		self.auth.set_item(PAM.PAM_USER, user)
		self.auth.set_item(PAM.PAM_CONV,pam_conv)
		try:
			self.auth.authenticate()
			self.auth.acct_mgmt()
			return True
		except Exception as e:
			return False
