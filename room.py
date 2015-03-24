import urllib2
import json
from datetime import datetime
from time import sleep
import wave, sys, pyaudio

BASE_URL = 'http://labs.library.gvsu.edu/display/getRoomAvailability.php?roomId='

def checkRoom(id):
	results = urllib2.urlopen(BASE_URL + str(id)).read()
	print results
	reservation = json.loads(results)
	reservation_id = reservation['ReservationId']['0']
	end = reservation['TimeEnd'].split(':')
	now = datetime.now()
	end = datetime(now.year,now.month,now.day,int(end[0]),int(end[1]))
	remaining = (end-now).seconds/60
	return remaining, reservation_id

def beep():
	wf = wave.open('beep.wav')
	p = pyaudio.PyAudio()
	chunk = 1024
	stream = p.open(format =
	                p.get_format_from_width(wf.getsampwidth()),
	                channels = wf.getnchannels(),
	                rate = wf.getframerate(),
	                output = True)
	data = wf.readframes(chunk)
	while data != '':
	    stream.write(data)
	    data = wf.readframes(chunk)
def main():
	with open('roomid.txt') as f:
		room_id = int(f.read())
	last_id = 0
	while True:
		try:
			minutes, reservation_id = checkRoom(room_id)
			if minutes < 15 and reservation_id != last_id:
				print reservation_id
				last_id = reservation_id
				beep()
			else:
				print minutes, reservation_id
			sleep(10)
		except KeyboardInterrupt:
			exit()
if __name__ == '__main__':
	main()