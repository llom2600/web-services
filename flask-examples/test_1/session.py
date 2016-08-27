import socket, ssl
import re
import time


CRLF = "\r\n" #carriage return, line feed

class sesh(object):
	def __init__(self, sessionParameters = None):
		
		self.s = None				#socket handle
		self.is_connected = False	
		
		if not sessionParameters:
			print "Session instance created with default parameters."
			self.host = None		  #remote host - address
			self.port = None		   #remote host  - port
		else:
			valid = self.validateSessionParameters(sessionParameters)
			if not valid:
				print "Invalid session parameters specified. Setting default."
				self.host = None
				self.port = None
			elif valid:
				self.host = sessionParameters['host']
				self.port = int(sessionParameters['port'])
				print "Setting remote host address...\n", self.host, ":", self.port
				
				if self.port == 443:
					self.SSL = True
				else:
					self.SSL = False
		
		
		#socket configuration settings
		self.is_blocking = False
		self.socket_timeout = 2.0
		self.socket_buffer_size = 4906

		
	
	def validateSessionParameters(self, sessionParameters):
		host_name_valid = re.compile(r'((www\.)?([A-Za-z0-9]+[\.])+[A-Za-z]+)')
		port_valid = re.compile(r'[1-9][0-9]?[0-9]?[0-9]?[0-9]?')
		#ip_address_valid = re.compile
		
		if sessionParameters['host']:
			m =re.search(host_name_valid, sessionParameters['host'])
			if m:
				if (len(m.group(0)) != len(sessionParameters['host'])):
					print "Invalid host name."
					return -1
		else:
			print 'Foreign host unspecified.'
			return -1
			
		if sessionParameters['port']:
			m = re.search(port_valid, sessionParameters['port'])
			if m:
				if (len(m.group(0)) != len(sessionParameters['port'])):
					print "Invalid port. Valid range is (1-65535), Input: ", sessionParameters['port']
					return -1
		else:
			print "Foreign port unspecified."
		
		return True
	
	
	#open standard socket (not SSL)
	def open(self):
		if(self.SSL): 
			return self.openSSL()

		# if not using SSL, set up standard socket
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setblocking(self.is_blocking)
		
		if not self.is_blocking:
			self.s.settimeout(self.socket_timeout)

		try:
			self.s.connect((self.host, self.port))
		except socket.timeout as e:
			return (-1)

		self.is_connected = True 		#set flag for successfully connected

		
	#open ssl socket
	def openSSL(self):
		context = ssl.create_default_context()

		self.s = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.host)
		
		self.s.setblocking(self.is_blocking)
		
		if not self.is_blocking:
			self.s.settimeout(self.socket_timeout)

		try:
			self.s.connect((self.host, self.port))
		except Exception as e:
			print "Exception: ", e
			return -1

		self.is_connected = True		#set flag for successfully connected
		self.socket_cert = self.s.getpeercert()
	
	
	
	def get(self, path):
		#reset response variables
		self.response_header = None
		self.response_body = None
		
		#create current request header given path on server
		self.request_header = [ "GET " + path + " HTTP/1.1",
												"Host: " + self.host + ":" + str(self.port),
				  	 							"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				  								"Accept-Language: en-US,en;q=0.8",
							  				]
		
		if not self.is_connected:
			print "No active connection. Cannot perform GET request."
			return -1

		'''
		if  (self.__cookie != "" and self.cookiesEnabled):
			header.append("Cookie: " + cookieString(self.__cookie))
		'''
	
		### need these two gaps for a properly formatted request #########
		self.request_header.append("")
		self.request_header.append("")
		########################################################

		self.request_header = CRLF.join(self.request_header)		#concatenate request header components		
		
		print "Sending:"
		print self.request_header
		
		self.s.send(self.request_header)										   #send GET request
		
		#local vars to store response data
		response = ""
		data = None

		while True:
			try:
				data = self.s.recv(self.socket_buffer_size)
			except Exception as e:
				if (data == None and response != ""):
					break
			if data:
				response += data
				data = None
			else:
				break
			
		header_data, _, body = response.partition(CRLF*2)

		self.response_header = header_data
		self.response_body = body

		#self.__cookie = parse_cookies(self.response, self.__cookie)

		return body

		
	def close(self):
		if (self.is_connected):
			print "Closing connection to ", self.host
			self.s.close()
			self.is_connected = False
		
				
				