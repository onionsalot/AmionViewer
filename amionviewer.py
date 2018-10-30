import tkinter as tk
from tkinter import ttk
from tkinter import *
from bs4 import BeautifulSoup
import calendar
import datetime
import time
from robobrowser import RoboBrowser
from pynput import mouse
from pynput import keyboard
from pynput.keyboard import Key, Controller
from configparser import ConfigParser
from PIL import Image, ImageTk
import os
import sys
import re

base_url = 'https://www.amion.com/'
browser = RoboBrowser()
browser.open(base_url)

# Get the signin form
signin_form = browser.get_form(action="cgi-bin/ocs")
# Fill it out
test = signin_form['Login'] = 'weiler1'
# Hit submit button
browser.submit_form(signin_form)


# Place the source info. No more URL just pass in data then display
source = str(browser.select)
soup = BeautifulSoup(source, 'lxml')

firstTable = soup.find('table', { 'cellpadding' : '2' })
obj=[]
for tableBody in firstTable.find_all('tr'):
	for firstElement in tableBody.find_all('td'):
		# print(firstTable)
		firstElement = firstElement.text
		# obj = [firstElement for i in range(32)]
		obj.append(firstElement)


# Function to split up an array into arrays of equal length
def chunks(l, n):
	# for item i in a range that is a length of l,
	for i in range(0, len(l), n):
		# Create an index range for l of n items:
		yield l[i:i+n]


''' Split into chunks of (number of days in the month) + 1.
	Reason for +1 is because of the 0th index.

	This is where we determine the current month and how many days are in the current month.
	In order to get the amount of days in the month, we need to use monthrange(YEAR, MONTH)
	To automate this process, we will be using the datetime function to get the current year
	and month to pass into monthrange. We will then be passing monthrange into the "chunk"
	function in order to separate our large array of items into smaller pieces. Items will be 
	split into chunks of (number of days in the month) + 1 due to having a 0th element. The point 
	of this is because each of the smaller teamList[] will basically represent a single team 
	along with the order of attendings.

	We will then further extract this to get a single team.
'''
getDateInfo = datetime.datetime.now()
currentYear = getDateInfo.year
currentMonth = getDateInfo.month
daysInMonth = calendar.monthrange(currentYear,currentMonth)[1]
print(daysInMonth)
teamList = list(chunks(obj, daysInMonth+1))
# pop method used to remove first element of teamList which is the DATES ONLY
teamList.pop(0)
print(teamList[0])

# Get the total count of the array
itemCount = len(teamList)
print(itemCount)

# Try and parse out elements of teamList and place into singleTeam then print.
try:
	singleTeam = teamList[0]
except IndexError:
	singleTeam = ""


# Get date, and check the singleItem for the date.
date = getDateInfo.day
print(singleTeam[1] + singleTeam[date])

'''NOTES:
	singleTeam represents an array of items going horizontal
	it takes the entire field from left to right
	Element 0 of the array will then always represent the team name
	Element 1 and onwards will show the current team for that day
	We pass in [date] into Element 1 in order to track down the team for 
	that day of the week. date variable is bound to the current date.
'''

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#					List of Attendings Dictionary
#-------------------------------------------------------------------
#-------------------------------------------------------------------
secondTable = soup.find_all('table', {'cellpadding': '2'})[1]

attendings= []
for getAttending in secondTable.find_all('font'):
	getAttending = getAttending.text
	attendings.append(getAttending)

print(len(attendings))
even = attendings[::2]
print(even)
odd = attendings[1::2]
print(odd)

attendingDict = dict(zip(odd,even))
print(attendingDict)
print(attendingDict["ES"])

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#					Config section
#-------------------------------------------------------------------
#-------------------------------------------------------------------
config = ConfigParser()
config.read('config.ini')

def getConfig():
	a_string_list = config.get('frames', 'key')
	deleteArray = a_string_list.split(',')
	return deleteArray

def write_file():
	config.write(open('config.ini', 'w'))

if not config.has_section('frames'):
	# Case new
	config.add_section('frames')
	deleteArray = []
	config.set('frames', 'key', 'placeholder')
	write_file()
elif config.has_section('frames'):
	# Case used
	deleteArray = getConfig()
	print(deleteArray)

deleteString = ""
#-------------------------------------------------------------------
#-------------------------------------------------------------------
#					GUI Elements
#-------------------------------------------------------------------
#-------------------------------------------------------------------


keyboard = Controller()
class ToggledFrame(tk.Frame):

	def __init__(self, parent, text="", text2="", *args, **options):
		tk.Frame.__init__(self, parent, *args, **options)

		self.show = tk.IntVar()
		self.show.set(1)

		self.title_frame = ttk.Frame(self)
		self.title_frame.pack(fill="x", expand=1)

		ttk.Label(self.title_frame, text=text).pack(side="left", fill="x", expand=1)
		self.currentTeamName = text
		self.currentAttendingName = text2
		self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='-', command=self.toggle,
											 variable=self.show, style='Toolbutton')
		self.toggle_button.pack(side="left")

		self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)
		self.sub_frame.pack(fill="x", expand=1)

		self.sub_toggle_button = tk.Button(self.sub_frame, text="x", width=1, command=self.delete)
		self.sub_toggle_button.pack(side= "right")

		self.sub_auto_button = tk.Button(self.sub_frame, text="%", width=2)
		self.sub_auto_button.pack(side= "left")

	def toggle(self):
		if bool(self.show.get()):
			self.sub_frame.pack(fill="x", expand=1)
			self.toggle_button.configure(text='-')
		else:
			self.sub_frame.forget()
			self.toggle_button.configure(text='+')

	def delete(self):
		deleteprompt = Popup(self, 1, self.currentTeamName).get_boolean()
		if deleteprompt:
			print(deleteprompt)
			self.sub_frame.forget()
			self.title_frame.forget()
			self.destroy()
			deleteArray.append(self.currentTeamName)
			deleteString= ','.join(deleteArray)
			config.set('frames', 'key', deleteString)
			with open('config.ini', 'w') as f:
				config.write(f)
		else:
			print(deleteprompt)

class Popup(tk.Toplevel):
	value = 0

	def __init__(self, master, callinfo, teaminfo):
		tk.Toplevel.__init__(self, master)

		x = root.winfo_x()
		y = root.winfo_y()

		w = self.winfo_width()
		h = self.winfo_height()

		dx = root.winfo_screenwidth()
		dy = root.winfo_screenheight()
		self.geometry("%dx%d+%d+%d" % (200, 200, x, y))

		if callinfo == 1:
			labeltext1 = 'Are you sure you want to delete ' + teaminfo
			labeltext2 = 'WARNING: To restore deleted teams, go to Help >> Reset my List'

		elif callinfo == 2:
			labeltext1= 'Would you like to reset your list?'
			labeltext2= 'Resetting will bring back all items that you had previously cleared'

		toplabel = tk.Label(self, height=1, font='Helvetica 14', text=labeltext1)
		toplabel.pack()

		warning = tk.Label(self, text=labeltext2)
		warning.pack()

		bottomFrame = Frame(self)
		bottomFrame.pack()
		btn = tk.Button(bottomFrame, text="OK", command=self.deleteframe)
		btn.pack(side=LEFT)
		btn = tk.Button(bottomFrame, text="CANCEL", command=self.canceldelete)
		btn.pack(side=LEFT)

		self.transient(root) #set to be on top of the main window
		self.grab_set() #hijack all commands from the master (clicks on the main window are ignored)
		root.wait_window(self) #pause anything on the main window until this one closes (optional)

	def deleteframe(self):
		self.value = 1
		self.destroy()

	def canceldelete(self):
		self.value = 0
		self.destroy()

	def get_boolean(self):
		return self.value


# ///////////////////////////////////////////////////////////////////////// Root Frame Setup
# /////////////////////////////////////////////////////////////////////////

root = tk.Tk()
root.title('test')
root.configure(background='black')
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
#root.resizable(0, 0)
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
x = (width/2) - (width/2)
y = (height/2)
root.geometry('%dx%d+%d+%d' % (width, 500, x, y))

# ///////////////////////////////////////////////////////////////////////// Frame setup
# /////////////////////////////////////////////////////////////////////////

def raiser(frame):
	print('test')
	frame.tkraise()


mainframe = tk.Frame(root)
mainframe.grid(row=0, column=0, sticky="nsew")

frame1 = tk.Frame(mainframe)
frame2 = tk.Frame(mainframe)
frame3 = tk.Frame(mainframe)
frame4 = tk.Frame(mainframe)
frame5 = tk.Frame(mainframe)

frame1.grid(row=0, column=0, sticky="nsew")
frame2.grid(row=0, column=1, sticky="nsew")
frame3.grid(row=0, column=2, sticky="nsew")
frame4.grid(row=0, column=3, sticky="nsew")
frame5.grid(row=0, column=4, sticky="nsew")

mainframe.grid_columnconfigure(0, weight=1, uniform="group1")
mainframe.grid_columnconfigure(1, weight=1, uniform="group1")
mainframe.grid_columnconfigure(2, weight=1, uniform="group1")
mainframe.grid_columnconfigure(3, weight=1, uniform="group1")
mainframe.grid_columnconfigure(4, weight=1, uniform="group1")
mainframe.grid_rowconfigure(0, weight=1)


aboutframe = tk.Frame(root, bg="blue")
aboutframe.grid(row=0, column=0, sticky="nsew")

aframe1 = tk.Frame(aboutframe)
aframe2 = tk.Frame(aboutframe)

aframe1.grid(row=0, column=0, sticky="nsew")
aframe2.grid(row=0, column=1, sticky="nsew")

aboutframe.grid_columnconfigure(0, weight=1, uniform="group1")
aboutframe.grid_columnconfigure(1, weight=1, uniform="group1")
aboutframe.grid_rowconfigure(0,weight=1)

raiser(mainframe)

# ///////////////////////////////////////////////////////////////////////// Main Frame
# /////////////////////////////////////////////////////////////////////////

i = 0
b = 0
currentColumn = [frame1, frame2, frame3, frame4, frame5]
colorWords = ['Blue', 'Red', 'Aqua', 'Purple', 'Green', 'Yellow']


def endswith(endvalue):
	# Check if current passed in value ends with a number or not
	m = re.search(r'\d+$', endvalue)
	# if the string ends in digits m will be a Match object, or None otherwise.
	if m is not None:
		print(endvalue + ' contains a digit')
		return 1


while i < itemCount:
	if not set(deleteArray).isdisjoint(teamList[i]):
		print('match detected. Skipping current addition')
		i += 1
	else:
		try:
			singleTeam = teamList[i]
		except IndexError:
			singleTeam = teamList[0]

		# endswith() function used to check if team has a numbered ending, signifying sickcall and removes it.
		if endswith(singleTeam[date]):
			singleTeam[date] = singleTeam[date][:-1]
			print(singleTeam[date])

		singleTeam = [attendingDict.get(item, item) for item in singleTeam]

		# Checks count of b and then split up the teams per frame
		if b == 5:
			b = 0

		# Checks if singleTeam contains keywords we can use to decorate the text
		for currentColor in colorWords:
			if currentColor in singleTeam[0]:
				setColor = currentColor
				break
			else:
				setColor = 'white'

		teamName = ToggledFrame(currentColumn[b], text=singleTeam[0], text2=singleTeam[date], relief="raised",
								borderwidth=4, bg=setColor)
		teamName.pack(fill="x", pady=2, padx=2, anchor="n")

		entry = ttk.Entry(teamName.sub_frame)
		entry.insert(0, singleTeam[date])
		entry.pack()

		b += 1
		i += 1

# ///////////////////////////////////////////////////////////////////////// About Frame
# /////////////////////////////////////////////////////////////////////////

backphoto=PhotoImage(file="back.png")
backbutton= Button(aframe1, image=backphoto, text="back", command=lambda: raiser(mainframe), height=50, width=150)
backbutton.grid(column=0, row=0)

alabel1 = tk.Label(aframe1, font=(None, 22), justify=tk.LEFT, padx=5,
				   text="About")
alabel1.grid(column=0, row=1)
alabel2 = tk.Label(aframe1, font=(None, 13), justify=tk.LEFT, padx=5, wraplength=y,
				   text="Summary:\nAmionViewer is a windows application built using Python and powered by amion.com, a site designed for physician scheduling." +
						"\n\nThe purpose of this application is to streamline the process of looking up physician schedules by showing only relevant information to the department looking for said information. Designed under the philosophy that less is more, only showing the relevant information to those looking for it should increase productivity and automate mundane tasks, leaving employees free to perform more important things.")
alabel2.grid(column=0, row=2)


atitlelabelr = tk.Label(aframe2, font=(None, 22), justify=tk.LEFT, padx=5,
						text="Dev Profiles")
atitlelabelr.grid(column=0, row=0)
alabel1r = tk.Label(aframe2, font=(None, 13), justify=tk.LEFT, padx=5,
					text="Trong Nguyen\nBeginner developer. Core functionality designer and project head. Began development on 10/03/2018.\n\nContact info: onionsinmypants@gmail.com")
alabel1r.grid(column=0, row=2)

atitlelabelr2 = tk.Label(aframe2, font=(None, 22), justify=tk.LEFT, padx=5,
						 text="App info")
atitlelabelr2.grid(column=0, row=3)
alabel2r = tk.Label(aframe2, font=(None, 13), justify=tk.LEFT, padx=5,
					text="App version: 1.0.0"
						 + "\nCode Audit: https://github.com/onionsinmypants/AmionViewer"
						 + "\nChangelog:\n")
alabel2r.grid(column=0, row=4)

# ///////////////////////////////////////////////////////////////////////// Top menu
# /////////////////////////////////////////////////////////////////////////

menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='New')
filemenu.add_command(label='Open...')
filemenu.add_separator()
filemenu.add_command(label='Exit', command=root.quit)
helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='Reset my List', command=lambda: deletePreferences())
helpmenu.add_separator()
helpmenu.add_command(label='About', command=lambda: raiser(aboutframe))
helpmenu.add_command(label='Check for Updates', command=lambda: raiser(aboutframe))

def deletePreferences():
	deleteprompt = Popup(root, 2, "").get_boolean()
	if deleteprompt:
		print(deleteprompt)
		open("config.ini", "w").close()
		python = sys.executable
		os.execl(python, python, * sys.argv)

	else:
		print(deleteprompt)

root.mainloop()
