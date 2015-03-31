import urllib2
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from time import sleep
from subprocess import call
from sys import stdout, argv
from os import getcwd
from collections import defaultdict

BASE_URL = 'http://gvsu.edu/reserve/files/cfc/functions.cfc?method=bookings&roomId={0}&startDate={1}&endDate={2}'
MINUTES = 59
PATH = getcwd() + '/'
SOUND = 'warning.wav'


def get_info_from_booking(booking):
	print booking
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

	xml = ET.fromstring(results)
	bookings = sorted(xml.findall('Data'),key=get_time)
	current = None
	
	for booking in bookings:
		booking.start_time = datetime.strptime(booking.find('TimeEventStart').text, '%Y-%m-%dT%H:%M:%S')
		booking.end_time = datetime.strptime(booking.find('TimeEventEnd').text, '%Y-%m-%dT%H:%M:%S')	
		
		if booking.start_time < now and now <= booking.end_time:
			print booking.find('BookingID').text
			return get_info_from_booking(booking)  


def get_time(booking):
	date = datetime.strptime(booking.find('TimeEventStart').text,'%Y-%m-%dT%H:%M:%S')
	return date

def play_sound(sound):
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
