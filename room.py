import urllib2
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from time import sleep
from subprocess import call
from os import getcwd
from collections import defaultdict

BASE_URL = 'http://gvsu.edu/reserve/files/cfc/functions.cfc?method=bookings&roomId={0}&startDate={1}&endDate={2}'
MINUTES = 10
PATH = getcwd() + '/'
SOUND = 'warning.wav'


def get_info_from_booking(booking):
	now = datetime.now()
	data = defaultdict(str)
	data['booking_id'] = booking.find('BookingID').text
	data['start'] = booking.start_time
	data['end'] = booking.end_time
	data['minutes_left'] = booking.end_time.minute - now.minute 
	data['reserved_by'] = booking.find('EventName').text.split(' - ')[0]
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
		if booking.start_time < now < booking.end_time:
			current = booking
	if current is not None:
		return get_info_from_booking(current) 


def get_time(booking):
	date = datetime.strptime(booking.find('TimeEventStart').text,'%Y-%m-%dT%H:%M:%S')
	return date

def play_sound(sound):
	call('aplay ' + PATH + sound, shell=True)

def main():
	with open(PATH + 'roomid.txt') as f:
		room_id = int(f.read())
	last_id = None
	last_reserved_by = None
	
	while True:
		try:
			room = get_room(room_id)
			if room['minutes_left'] < MINUTES and room['booking_id'] != last_id and room['reserved_by'] != last_reserved_by:
				last_id = room['booking_id']
				last_reserved_by = room['reserved_by']
				play_sound(SOUND)
			else:
				print room['minutes_left']
			sleep(10)
		except KeyboardInterrupt:
			exit()
if __name__ == '__main__':
	main()
