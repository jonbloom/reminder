import urllib2
import json
from datetime import datetime
from time import sleep
from subprocess import call
from os import getcwd
BASE_URL = 'http://labs.library.gvsu.edu/display/getRoomAvailability.php?roomId='
MINUTES = 10
PATH = getcwd() + '/'

def checkRoom(id):
	results = urllib2.urlopen(BASE_URL + str(id)).read()
	print (chr(27) + "[2J")		
	print results
	try:
		reservation = json.loads(results)
		reservation_id = reservation['ReservationId']['0']
		end = reservation['TimeEnd'].split(':')
		now = datetime.now()
		end = datetime(now.year,now.month,now.day,int(end[0]),int(end[1]))
		remaining = (end-now).seconds/60
	except:
		pass
	return remaining, reservation_id

def beep():
	call('aplay ' + PATH + 'warning.wav', shell=True)
def main():
	with open(PATH + 'roomid.txt') as f:
		room_id = int(f.read())
	last_id = 0
	while True:
		try:
			minutes_left, reservation_id = checkRoom(room_id)
			if minutes_left < MINUTES and reservation_id != last_id:
				print reservation_id
				last_id = reservation_id
				beep()
			else:
				print minutes_left, reservation_id
			sleep(10)
		except KeyboardInterrupt:
			exit()
if __name__ == '__main__':
	main()
