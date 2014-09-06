from twilio.rest import TwilioRestClient 
from email.utils import parsedate
from datetime import datetime, timedelta
import time
import ConfigParser
import logging

# set up the log file
LOG_FILENAME = 'checksms.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

# read config file
config = ConfigParser.ConfigParser()
config.read('config.ini')

phonebook = config.get('users', 'numbers').split(',')
passcodes = config.get('main', 'passcode').split(',')
defaultto = config.get('main', 'defaultto')
defaultfrom = config.get('main', 'defaultfrom')

# put your own credentials here 
ACCOUNT_SID = config.get('main', 'ACCOUNT_SID')
AUTH_TOKEN = config.get('main', 'AUTH_TOKEN')
 
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 

while True:

	# sleep 60 seconds
	time.sleep(60) 

	# get the current time in UTC format
	now = datetime.utcnow()

	messagefound = False

	#for p in phonebook:

	messages = client.messages.list(
		#from_ = p,  
		after = ( now - timedelta(minutes = 1) )
	) 
	 
	for m in messages: 

		if any( m.from_ in p for p in phonebook):

		then = datetime.fromtimestamp(time.mktime(parsedate(m.date_sent)))

		# message was received with delta
		if ( ( now - then ) <= timedelta(minutes = 1) ) and ( ( now - then ) >= timedelta(minutes = 0) ):
			
			phrase = m.body.lower()

			# check if it matches passcode
			if any( phrase in codes for codes in passcodes):
				logging.info( "%s - %s @ %s ", m.from_, m.body, m.date_sent )

				# TODO: remove debug info
				print m.date_sent, " - from ", m.from_, " - ", m.body, " delta: ", ( now - then )

				try:
					# execute trigger here
					client.messages.create(
						to=m.from_, 
						from_=defaultfrom, 
						body="I got your message. Open sesame!",  
					)
				except:
					client.messages.create(
						to=defaultto, 
						from_=defaultfrom, 
						body=m.from_,  
					)
					pass

				messagefound = True
				break

	if messagefound:
		break
