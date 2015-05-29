Raspberry Pi Room Reservation Expiration Reminder (of Doom!)
========

To set up a new Raspberry Pi, you'll need a few things:

1. The EMS room ID
2. The Raspberry Pi
3. A monitor, keyboard, Micro USB cable and an ethernet cable
4. A bit of Linux knowledge

Setup Instructions
=====
1. Connect the Raspberry Pi to a monitor, then connect the keyboard, ethernet, and Micro USB cables.
2. Install Raspbian via Noobs if not already installed. Instructions [here](https://www.raspberrypi.org/help/noobs-setup/).
3. Once you're booted to the desktop, press `Ctrl` + `Alt` + `F1` to access a terminal. Login with the username `pi` and the password `raspberry` if necessary.
4. Run the command `sudo raspi-config`.
5. While in Raspi-Config, make sure you have the correct timezone selected.
6. Change the boot options to console from desktop.
7. Exit Raspi-Config.
8. Run the following commands:
  1. `cd /tmp`
  2. `wget https://bootstrap.pypa.io/get-pip.py`
  3. `sudo python get-pip.py`
  4. `sudo pip install APScheduler`
  5. `git clone git://github.com/gvsulib/reminder.git`
  6. `cd ~/reminder`
  6. `nano`
9. Add the super secret raspberry pi tracker password in the format
  * `pw = 'supersecretraspberrypitrackerpassword'`
10. Hit `Ctrl` + `X`, then `y`, and save the file as `secret.py`.
11. Run the command `sudo nano /etc/rc.local`.
12. Add the following line to the end of the file before `exit 0` replacing `{EMSID}` with the EMS ID of the room the Raspberry Pi will be located:
  * `sudo python /home/pi/reminder/room.py {EMSID} &`
13. Hit `Ctrl` + `X`, then `y`, and save the file as `rc.local`.
14. You should now be able to issue a `sudo reboot` and see the Raspberry Pi's information populate [here](https://labs.library.gvsu.edu/raspberrypi-reporter/admin.php).
15. If everything went right, you're done. Go hide the Raspberry Pi somewhere in the room where it won't be tampered with.