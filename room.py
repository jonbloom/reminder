from __future__ import print_function
import urllib
import xml.etree.ElementTree as ET
import fcntl, socket, struct
from datetime import datetime, timedelta
from time import sleep
from subprocess import call
from sys import stdout, argv
from collections import defaultdict
from itertools import tee, islice, chain, izip
from apscheduler.schedulers.background import BackgroundScheduler

import logging
logging.basicConfig(level=logging.CRITICAL)

from secret import pw

sched = BackgroundScheduler()
sched.start()

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
	url = 'http://labs.library.gvsu.edu/raspberrypi-reporter/report.php?' + urllib.urlencode(data)
	urllib.urlopen(url)

def get_info_from_booking(booking, room_id):
	now = datetime.now()
	data = defaultdict(str)
	data['room_id'] = room_id
	data['booking_id'] = booking.find('BookingID').text
	data['start'] = booking.start_time
	data['end'] = booking.end_time
	data['minutes_left'] = booking.end_time.minute - now.minute 
	data['reserved_by'] = booking.find('EventName').text.split(' - ')[0]
	data['room_name'] = booking.find('RoomDescription').text
	return data

def get_room(room_id):
	ten_minutes = timedelta(minutes=10)
	now = datetime.now()
	now_str = now.strftime('%Y-%m-%d')
	url = BASE_URL.format(*[room_id,now_str,now_str])
	results = urllib.urlopen(url).read()
	send_details(room_id)

	xml = ET.fromstring(results)
	bookings = sorted(xml.findall('Data'),key=get_time)
	
	for last_booking, current_booking, next_booking in prev_next(bookings):
		current_booking.start_time = datetime.strptime(current_booking.find('TimeEventStart').text, '%Y-%m-%dT%H:%M:%S')
		current_booking.end_time = datetime.strptime(current_booking.find('TimeEventEnd').text, '%Y-%m-%dT%H:%M:%S')
		
		if current_booking.end_time >= now:
			if next_booking is None or current_booking.find('EventName').text.split(' - ')[0] != next_booking.find('EventName').text.split(' - ')[0]: 
				
					job = sched.add_job(
						play_sound,
						'date',
						run_date=current_booking.end_time-ten_minutes,
						args=[SOUND,get_info_from_booking(current_booking, room_id)],
						id=current_booking.find('BookingID').text,
						replace_existing=True)
					print('start: {0} end: {1} reserved by: {2} {3}'.format(
						current_booking.start_time,
						current_booking.end_time,
						current_booking.find('EventName').text.split(' - ')[0],
						'Reminded' if current_booking.end_time < now else ''))
					

def get_time(booking):
	date = datetime.strptime(booking.find('TimeEventStart').text,'%Y-%m-%dT%H:%M:%S')
	return date

def prev_next(some_iterable):
	# http://stackoverflow.com/a/1012089/2961967
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)

def play_sound(sound, room):
	call('amixer set PCM,0 92%', shell=True)
	call('aplay ' + PATH + sound, shell=True)
	
	room['pw'] = pw
	url = 'http://labs.library.gvsu.edu/raspberrypi-reporter/log.php?' + urllib.urlencode(room)
	urllib.urlopen(url)
def main():
	room_id = argv[1]
	while True:
		try:
			room = get_room(room_id)
			sleep(10)
		except KeyboardInterrupt as e:
			exit()
		except Exception as e:
			print (e)
if __name__ == '__main__':
	main()
