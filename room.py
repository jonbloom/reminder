import urllib2
import xml.etree.ElementTree as ET
import json
import fcntl, socket, struct
from datetime import datetime
from time import sleep
from subprocess import call
from sys import stdout, argv
from os import getcwd
from collections import defaultdict

from secret import pw



BASE_URL = 'http://gvsu.edu/reserve/files/cfc/functions.cfc?method=bookings&roomId={0}&startDate={1}&endDate={2}'
MINUTES = 10
PATH = '/home/pi/reminder/'
SOUND = 'warning.wav'

def send_details(room_id):
	data = dict()
	# http://stackoverflow.com/a/4789267/2961967 Gets MAC Address
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	mac_address = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', 'eth0'))
	data['mac'] = ':'.join(['%02x' % ord(char) for char in mac_address[18:24]])
	# http://stackoverflow.com/a/166589/2961967 Gets IP address
	s.connect(('8.8.8.8',80))
	data['ip'] = s.getsockname()[0]
	s.close()

	data['room_id'] = room_id
	data['pw'] = pw

	url = 'http://labs.library.gvsu.edu/raspberry_pi/report.php?' + urllib2.urlencode(data)
	req = urllib2.Request(url)
	urllib2.urlopen(req)

def get_info_from_booking(booking):
	now = datetime.now()
	data = defaultdict(str)
	data['booking_id'] = booking.find('BookingID').text
	data['start'] = booking.start_time
	data['end'] = booking.end_time
	data['minutes_left'] = booking.end_time.minute - now.minute 
	data['reserved_by'] = booking.find('EventName').text.split(' - ')[0]
	data['room_name'] = booking.find('RoomDescription').text
	return data

def get_room(room_id):
	now = datetime.now()
	now_str = now.strftime('%Y-%m-%d')
	url = BASE_URL.format(*[room_id,now_str,now_str])
	results = urllib2.urlopen(url).read()
	send_details(room_id)

	xml = ET.fromstring(results)
	bookings = sorted(xml.findall('Data'),key=get_time)
	current = None
	
	for booking in bookings:
		booking.start_time = datetime.strptime(booking.find('TimeEventStart').text, '%Y-%m-%dT%H:%M:%S')
		booking.end_time = datetime.strptime(booking.find('TimeEventEnd').text, '%Y-%m-%dT%H:%M:%S')	
		
		if booking.start_time < now and now <= booking.end_time:
			return get_info_from_booking(booking)  


def get_time(booking):
	date = datetime.strptime(booking.find('TimeEventStart').text,'%Y-%m-%dT%H:%M:%S')
	return date

def play_sound(sound):
	call('amixer set PCM,0 92%', shell=True)
	call('aplay ' + PATH + sound, shell=True)

def main():
	room_id = argv[1]
	last_id = None
	last_reserved_by = None
	printed = False
	while True:
		try:
			room = get_room(room_id)
			if not printed:
				print room['room_name']
				printed = True
			if room['minutes_left'] < MINUTES and room['booking_id'] != last_id and room['reserved_by'] != last_reserved_by:
				last_id = room['booking_id']
				last_reserved_by = room['reserved_by']
				play_sound(SOUND)
			else:
				stdout.write(str(room['minutes_left']))
				stdout.flush()
				stdout.write('\r')
				stdout.flush()
			sleep(10)
		except KeyboardInterrupt as e:
			exit()
		except:
			pass
if __name__ == '__main__':
	main()
