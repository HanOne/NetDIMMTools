#!/usr/bin/python2
# Written by Capane.us
# Modified by Han

import os, collections, signal, sys, subprocess, socket
import triforcetools
from systemd import daemon
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from time import sleep
from subprocess import call
from ConfigParser import SafeConfigParser

# We are up, so tell systemd
daemon.notify("READY=1")

# Define restart program
def restart_program():
	# Restarts the current program.
	# Note: this function does not return. Any cleanup action (like
	# saving data) must be done before calling this function.
    python = sys.executable
    os.execl(python, python, * sys.argv)

# Define a signal handler to turn off LCD before shutting down
def handler(signum = None, frame = None):
    lcd = Adafruit_CharLCDPlate()
    lcd.clear()
    lcd.stop()
    sys.exit(0)
signal.signal(signal.SIGTERM , handler)

# Initialize LCD
lcd = Adafruit_CharLCDPlate()
lcd.begin(16, 2)
lcd.message("NetDIMM Tools\nVersion 2.0")

# Initialize parameters ---------- ---------- ----------
parser=SafeConfigParser()

# Read parameters from file ---------- ---------- ----------
config_file_read="./netdimmtools.cfg"
config_file_verify=""
while config_file_verify != config_file_read:
	if os.path.isfile(config_file_read):
		config_file_verify=config_file_read
		parser.read(config_file_read)
		config_file_read=parser.get("Parameters", "Parameters File")
	else:
		# No config available
		lcd.clear()
		lcd.message("Error: Config\nUnavailable!")
		sleep (1)
		lcd.clear()
		lcd.message("Error: Programm\nCanceled!")
		sleep (1)		
		print config_file_verify
		print config_file_read
		
targets_list=eval(parser.get("Parameters", "Targets"))
startup_wait=int(parser.get("Parameters", "Startup Wait"))
targets_discover=int(parser.get("Parameters", "Targets Discover"))
sleep_message=int(parser.get("Parameters", "Sleep Message"))
sleep_error=int(parser.get("Parameters", "Sleep Error"))

path_bios_naomi=parser.get("Pathes", "BIOS Naomi")
path_bios_naomi2 = parser.get("Pathes", "BIOS Naomi2")
path_roms_atomiswave = parser.get("Pathes", "ROMS Atomiswave")
path_roms_naomi = parser.get("Pathes", "ROMS Naomi")
path_roms_naomi2 = parser.get("Pathes", "ROMS Naomi2")
path_roms_chihiro = parser.get("Pathes", "ROMS Chihiro")
path_roms_triforce = parser.get("Pathes", "ROMS Triforce")
bios_naomi=eval(parser.get("ROMS", "BIOS Naomi"))
bios_naomi2=eval(parser.get("ROMS", "BIOS Naomi2"))
roms_atomiswave=eval(parser.get("ROMS", "ROMS Atomiswave"))
roms_naomi=eval(parser.get("ROMS", "ROMS Naomi"))
roms_naomi2=eval(parser.get("ROMS", "ROMS Naomi2"))
roms_chihiro=eval(parser.get("ROMS", "ROMS Chihiro"))
roms_triforce=eval(parser.get("ROMS", "ROMS Triforce"))

# Static parameters ---------- ---------- ----------
commands_list = ["Ping Target", "Reset Target", "Select Target", "Restart Program", "Restart System", "Shutdown System"]
commands_list_emergency=["Restart Program", "Restart System", "Shutdown System"]
ping_target_available=1		# enable command "Ping Target" (ping active target)
reset_target_available=1	# enable command "Reset Target" (some games only accept in service menu)
select_target_available=1	# enable command "Select Target" (select target from available targets)
restart_program_available=1	# enable command "Restart Program" (restart pyhton program)
restart_system_available=1	# enable command "Restart System" (restart raspberry pi)
shutdown_system_available=1	# enable command "Shutdown System" (shutdown raspberry pi)

sleep (sleep_message)
# Startup wait ---------- ---------- ----------
# Wait for [OK] at startup
if startup_wait is 1:
	lcd.setCursor(12, 1)
	lcd.message("[OK]")
	pressedButtons=[]
	while lcd.SELECT not in pressedButtons:
		# Handle SELECT
		if lcd.buttonPressed(lcd.SELECT):
			pressedButtons.append(lcd.SELECT)
			if lcd.SELECT in pressedButtons:
				pressedButtons.append(lcd.SELECT)
				lcd.clear()

# Blink ON
lcd.ToggleBlink()
				
# Scan targets ---------- ---------- ----------
lcd.clear()
lcd.message("Scanning\nTargets...")

if targets_discover is 1:
	#Purge unavailable targets
	targets_found=[]
	for key,value in targets_list.iteritems():
		response = os.system("ping -c 1 "+targets_list[key])
		if response == 0:
			targets_found.append(value), ", "
	targets_list=targets_found

# Blink OFF
lcd.ToggleBlink()

if len(targets_list) is 0:
	lcd.clear()
	lcd.message("Error: Targets\nUnavailable!")
	sleep(sleep_error)
	targets_available=0
else:
	targets_available=1
	
# Blink ON
lcd.ToggleBlink()

# Scan roms ---------- ---------- ----------
lcd.clear()
lcd.message ("Scanning\nROMS...")

for key, value in bios_naomi.iteritems():
	bios_naomi[key] = path_bios_naomi+value
for key, value in bios_naomi2.iteritems():
	bios_naomi2[key] = path_bios_naomi2+value
for key, value in roms_atomiswave.iteritems():
	roms_atomiswave[key] = path_roms_atomiswave+value
for key, value in roms_naomi.iteritems():
	roms_naomi[key] = path_roms_naomi+value
for key, value in roms_naomi2.iteritems():
	roms_naomi2[key] = path_roms_naomi2+value
for key, value in roms_chihiro.iteritems():
	roms_chihiro[key] = path_roms_chihiro+value
for key, value in roms_triforce.iteritems():
	roms_triforce[key] = path_roms_triforce+value

roms_list=dict(bios_naomi.items() + bios_naomi2.items() + roms_atomiswave.items() + roms_naomi.items() + roms_naomi2.items() + roms_chihiro.items() + roms_triforce.items())

# Purge game dictionary of game files that can't be found
roms_missing=[]
for key, value in roms_list.iteritems():
    if not os.path.isfile(value):
        roms_missing.append(key)
for missing_rom in roms_missing:
    del roms_list[missing_rom]

# Blink OFF
lcd.ToggleBlink()

if len(roms_list) is 0:
	lcd.clear()
	lcd.message("Error: ROMS\nUnavailable!")
	sleep(sleep_error)
	roms_available=0
else:
	roms_available=1

# Mode 1 = Games
# Mode 2 = Commands
mode_2_available = 1
# Reduced menu items if no roms or not targets found
if roms_available is 0 or targets_available is 0:
	mode_1_available = 0
else:
	mode_1_available = 1

# Reduced options if no targets found
if targets_available is 0:
	commands_list=commands_list_emergency	# Enable reduced commands
	ping_target_available=0					# disable command "Ping Target"
	reset_target_available=0				# disable command "Reset Target"
	select_target_available=0				# disable command "Select Target"

# Display active mode ---------- ---------- ----------
lcd.clear()
if mode_1_available is 0:
 	# No ROMS found, GOTO Mode 2
	iterator  = iter(commands_list)
	selection = iterator.next()
	mode = "commands"	
	mode_active=2
	lcd.message(selection)
else:
    iterator  = iter(collections.OrderedDict(sorted(roms_list.items(), key=lambda t: t[0])))
    selection = iterator.next()
    mode = "games"
    mode_active=1
    lcd.message(selection)

# Start Loop  ---------- ---------- ----------
pressedButtons=[]
current_ip = 0
while True:
	# Handle SELECT
	if lcd.buttonPressed(lcd.SELECT):
		if lcd.SELECT not in pressedButtons:
			pressedButtons.append(lcd.SELECT)
			if selection is "Select Target" and select_target_available is 1:
					current_ip += 1	
					if current_ip >= len(targets_list):
						current_ip = 0
					lcd.message("\n"+targets_list[current_ip])
			elif selection is "Ping Target" and ping_target_available is 1:
					lcd.clear()
					lcd.ToggleBlink()
					lcd.message("Pinging...\n"+targets_list[current_ip])
					lcd.setCursor(10, 0)
					response = os.system("ping -c 1 "+targets_list[current_ip])
					lcd.clear()
					lcd.ToggleBlink()
					if response == 0:
						lcd.message("Success!")
					else:
						lcd.message("Error:\nPing Failed!")
					sleep(sleep_error)
					lcd.clear()
					lcd.message(selection)
			elif selection is "Reset Target" and reset_target_available is 1:
					lcd.clear()
					lcd.ToggleBlink()
					lcd.message("Connecting...")
					#lcd.setCursor(13, 0)
					try:
						triforcetools.connect(targets_list[current_ip], 10703)
					except:
						lcd.clear()
						lcd.ToggleBlink()
						lcd.message("Error:\nConnect Failed!")
						sleep(sleep_error)
						lcd.clear()
						lcd.message(selection)
						continue
					
					lcd.clear()
					lcd.message("Resetting...")
					#lcd.setCursor(12, 0)
				
					triforcetools.HOST_SetMode(0, 1)
					triforcetools.SECURITY_SetKeycode("\x00" * 8)
					triforcetools.HOST_Restart()
					triforcetools.TIME_SetLimit(10*60*1000)
					triforcetools.disconnect()
			
					lcd.clear()
					lcd.ToggleBlink()
					lcd.message("Reset Complete!")
					sleep(sleep_message)
					lcd.clear()
					lcd.message(selection)
			
			elif selection is "Restart Program" and restart_program_available is 1:
				lcd.clear()
				lcd.ToggleBlink()
				lcd.message("Restarting...")
				#lcd.setCursor(13, 0)
				sleep(sleep_message)
				lcd.clear()
				lcd.ToggleBlink()
				lcd.stop()
				restart_program()
			
			elif selection is "Shutdown System" and shutdown_system_available is 1:
				lcd.clear()
				lcd.ToggleBlink()
				lcd.message("Shutting Down...")
				#lcd.setCursor(16, 0)
				sleep(sleep_message)
				lcd.clear()
				lcd.ToggleBlink()
				lcd.stop()
				sleep(1)
				call(["shutdown", "-h", "now"])

			elif selection is "Restart System" and restart_system_available is 1:
				lcd.clear()
				lcd.ToggleBlink()
				lcd.message("Restarting...")
				#lcd.setCursor(13, 0)
				sleep(sleep_message)
				lcd.clear()
				lcd.stop()
				call(["shutdown", "-r", "now"])	

			else:
				if targets_available is 0:
					lcd.clear()
					lcd.message("Error: Targets\nUnavailable!")
					sleep(sleep_error)
					lcd.clear()
					lcd.message(selection)
				else:
					#Transfer game
					lcd.clear()
					lcd.ToggleBlink()
					lcd.message("Connecting...")
											
					try:
						triforcetools.connect(targets_list[current_ip], 10703)
					except:
						lcd.clear()
						lcd.ToggleBlink()
						lcd.message("Error:\nConnect Failed!")
						sleep(sleep_error)
						lcd.clear()
						lcd.message(selection)
						continue

					lcd.clear()
					lcd.message("Sending...")
					triforcetools.HOST_SetMode(0, 1)
					triforcetools.SECURITY_SetKeycode("\x00" * 8)
					triforcetools.DIMM_UploadFile(roms_list[selection])
					triforcetools.HOST_Restart()
					triforcetools.TIME_SetLimit(10*60*1000)
					triforcetools.disconnect()
	
					lcd.clear()
					lcd.ToggleBlink()
					lcd.message("Transfer\nComplete!")
					sleep(sleep_message)
					lcd.clear()
					lcd.message(selection)

	elif lcd.SELECT in pressedButtons:
		pressedButtons.remove(lcd.SELECT)

	# Handle LEFT
	if lcd.buttonPressed(lcd.LEFT):
		if lcd.LEFT not in pressedButtons and mode_1_available is 1 and mode_active is 2:
			pressedButtons.append(lcd.LEFT)
			mode      = "games"
			iterator  = iter(collections.OrderedDict(sorted(roms_list.items(), key=lambda t: t[0])))
			selection = iterator.next()
			previous  = None
			lcd.clear()
			lcd.message("Games")
			sleep(sleep_message)
			lcd.clear()
			lcd.message(selection)            
			mode_active=1
			
	elif lcd.LEFT in pressedButtons:
		pressedButtons.remove(lcd.LEFT)

	# Handle RIGHT
	if lcd.buttonPressed(lcd.RIGHT) and mode_2_available is 1 and mode_active is 1:
		if lcd.RIGHT not in pressedButtons and mode_2_available is 1 :
			pressedButtons.append(lcd.RIGHT)
			mode      = "commands"
			iterator  = iter(commands_list)
			selection = iterator.next()
			previous  = None
			lcd.clear()
			lcd.message("Commands")
			sleep(sleep_message)
			lcd.clear()
			lcd.message(selection)
			mode_active=2
			
	elif lcd.RIGHT in pressedButtons:
		pressedButtons.remove(lcd.RIGHT)

	# Handle UP
	if lcd.buttonPressed(lcd.UP):
		if lcd.UP not in pressedButtons and previous != None:
			pressedButtons.append(lcd.UP)
			if mode is "games":
				iterator = iter(collections.OrderedDict(sorted(roms_list.items(), key=lambda t: t[0])))
			else:
				iterator = iter(commands_list)
			needle = iterator.next()
			selection = previous
			previous = needle
			while selection != needle and selection != previous:
				previous = needle
				try:
					needle = iterator.next()
				except StopIteration:
					break
			lcd.clear()
			lcd.message(selection)                
	
	elif lcd.UP in pressedButtons:
		pressedButtons.remove(lcd.UP)

	# Handle DOWN
	if lcd.buttonPressed(lcd.DOWN):
		if lcd.DOWN not in pressedButtons:
			pressedButtons.append(lcd.DOWN)            
			previous = selection
			try:
				selection = iterator.next()
			except StopIteration:
				if mode is "games":
					iterator = iter(collections.OrderedDict(sorted(roms_list.items(), key=lambda t: t[0])))
				else:
					iterator = iter(commands_list)
				selection = iterator.next()
			lcd.clear()
			lcd.message(selection)
	
	elif lcd.DOWN in pressedButtons:
		pressedButtons.remove(lcd.DOWN)
