from flask import Flask, render_template
from session import *
import urllib
import re
import numpy

foreign_host = 'www.youtube.com'
foreign_port = '443'

linkPath = "/watch?v=LAYYDjaPsOQ"
CRLF = "\r\n" #carriage return, line feed

ITAG_FMT = {
'17': ['3GP','144p'],
'36': ['3GP','240p'],
'5': ['FLV','240p'],
'18':['MP4','360p'],
'22':['MP4','720p'],
'43':['WEBM','360p'],
	
#video ONLY itags
'160':['MP4','144p'],
'133':['MP4','240p'],
'134':['MP4','360p'],
'135':['MP4','480p'],
'136':['MP4','720p'],
'298':['MP4','1080p'],
'137':['MP4','1440p'],
'299':['MP4','2160p-2304p'],
'264':['MP4','2160p-4320p'],
'266':['MP4','144p'],
'138':['MP4','144p'],

'278':['WEBM','144p'],
'242':['WEBM','240p'],
'243':['WEBM','360p'],
'244':['WEBM','480p'],
'247':['WEBM','720p'],
'248':['WEBM','1080p'],
'271':['WEBM','1440p'],
'313':['WEBM','2160p'],
'302':['WEBM','720p HFR'],
'303':['WEBM','1080p HFR'],
'308':['WEBM','1440p HFR'],
'315':['WEBM','2160p HFR'],

#audio only itags (DASH)
'140':['M4A','128'],
'141':['M4A','256'],
'171':['WEBM','128'],
'249':['WEBM','48'],
'250':['WEBM','64'],
'251':['WEBM','160']

}


app = Flask(__name__)

@app.route('/')
def serveLinks():
	linkString = "a bunch of links"
	
	sessionParameters = {
	'host': foreign_host,
	'port': foreign_port
	}
	
		
	request_session = sesh(sessionParameters)	
	status = request_session.open()
	
	if request_session.is_connected:
		print "Successfully connected to: ", foreign_host
	
	request_session.get(linkPath)	
	
	if request_session.response_body != None:
		response_body = decodeResponse(request_session.response_body)
		directLinks = getLinks(response_body)
	
	linkList = []
	if directLinks:
		for i in range(len(directLinks)):
			#print "------------------------------------------------------"
			linkItem = dict(url=directLinks[i][0], filetype=directLinks[i][1][0], quality=directLinks[i][1][1])
			linkList.append(linkItem)
			#print "Format: ", directLinks[i][1][0], ":", directLinks[i][1][1]

	
	request_session.close()
	return render_template("links.html", links=linkList)


def decodeResponse(response_body):
	chunk = re.compile(r'\r\n[0-9A-Fa-f]+\r\n', flags = re.MULTILINE)
	m = re.findall(chunk, response_body)
	response_body = re.sub(chunk, "", response_body)
	return response_body


def getLinks(response_body):
	link_0 = re.compile(r'http[s]?://r[^;]+', flags=re.DOTALL | re.MULTILINE)
	
	#format detection regex (format codes are on top)
	itag_detection = re.compile(r'itag[\=][0-9][0-9]?[0-9]?', flags = re.DOTALL | re.MULTILINE)	
	
	response_body = urllib.unquote(response_body)
	m = re.findall(link_0, response_body)
	
	linkCount = 0
	linkList = []
	
	if m:
		for i in range(len(m)):
			m[i] = m[i].split(r'\u0026')
			for j in range(len(m[i])):
				has_itag = re.search(itag_detection, m[i][j])
				if has_itag:
					linkCount += 1
					itag_code = has_itag.group(0)[5:]
					print has_itag.group(0)
					itag_format = ITAG_FMT[itag_code]
					linkList.append([m[i][0], itag_format])
	
	if linkCount == 0:
		print "Error in formatting, probably due to encoding issue... try request again."
		return False
	
	return linkList


if __name__ == "__main__":
	app.run(port=8000, debug=False)
	
	