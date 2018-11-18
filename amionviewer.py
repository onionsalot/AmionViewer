import tkinter as tk
from tkinter import ttk
from tkinter import *
from bs4 import BeautifulSoup
import calendar
from datetime import datetime, timedelta
from robobrowser import RoboBrowser
from pynput.keyboard import Key, Controller
from configparser import ConfigParser
import os
import sys
import re
import urllib.request

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
obj = []
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
getDateInfo = datetime.now()

# These follow variables are used to see set the dates for each tab created.
dateVarToday = getDateInfo.strftime("	Today: %m/%d	")  # Formatted date for : Today
dateVarTmr = (getDateInfo + timedelta(days=1)).strftime("	Tomorrow: %m/%d	")  # Formatted date for : Tomorrow
dateVarNext = (getDateInfo + timedelta(days=1)).strftime("	Following: %m/%d/%Y	")  # Formatted date for : Next

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

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 					List of Attendings Dictionary
# -------------------------------------------------------------------
# -------------------------------------------------------------------
secondTable = soup.find_all('table', {'cellpadding': '2'})[1]

attendings = []
for getAttending in secondTable.find_all('font'):
	getAttending = getAttending.text
	attendings.append(getAttending)

print(len(attendings))
even = attendings[::2]
print(even)
odd = attendings[1::2]
print(odd)

attendingDict = dict(zip(odd, even))
print(attendingDict)
print(attendingDict["ES"])

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 					Config section
# -------------------------------------------------------------------
# -------------------------------------------------------------------
config = ConfigParser()
config.read('config.ini')


def getConfig():
	a_string_list = config.get('frames', 'key')
	deleteArray = a_string_list.split(',')
	return deleteArray


def writeFile():
	config.write(open('config.ini', 'w'))


if not config.has_section('frames'):
	# Case new
	config.add_section('frames')
	deleteArray = []
	config.set('frames', 'key', 'placeholder')
	writeFile()
elif config.has_section('frames'):
	# Case used
	deleteArray = getConfig()
	print(deleteArray)

deleteString = ""
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 					GUI Elements
# -------------------------------------------------------------------
# -------------------------------------------------------------------

# ///////////////////////////////////////////////////////////////////////// Root Frame Setup
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

root = tk.Tk()
root.title('test')

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# root.resizable(0, 0)
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
x = (width/2) - (width/2)
y = (height/2)
root.geometry('%dx%d+%d+%d' % (width, 500, x, y))

# ///////////////////////////////////////////////////////////////////////// Frame setup
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

''' NOTES:
	raiser method used to "raise" the frame forward. The idea ia that all frames are loaded upon setup, and once it is loaded,
	the main frame will be passed onto raiser which will put the rest of the frames in the background. When the user
	clicks on an item that requires a second frame, the raiser method will be called and it will raise the frame forward.
'''


def raiser(frame):
	frame.tkraise()


''' NOTES:
	CreateWindow is used to create the window along with a frame within the window to store items within. FrameCreation 
	can be called to return the windows that are created.
'''


class CreateWindow(tk.Frame):

	def __init__(self, parent, frametype, *args, **options):
		if frametype == 0:

			tk.Frame.__init__(self, parent)

			self.grid_columnconfigure(0, weight=1, uniform="group1")
			self.grid_columnconfigure(1, weight=1, uniform="group1")
			self.grid_columnconfigure(2, weight=1, uniform="group1")
			self.grid_columnconfigure(3, weight=1, uniform="group1")
			self.grid_columnconfigure(4, weight=1, uniform="group1")
			self.grid_rowconfigure(0, weight=1)

			self.frame1 = tk.Frame(self)
			self.frame2 = tk.Frame(self)
			self.frame3 = tk.Frame(self)
			self.frame4 = tk.Frame(self)
			self.frame5 = tk.Frame(self)

			self.frame1.grid(row=0, column=0, sticky="nsew")
			self.frame2.grid(row=0, column=1, sticky="nsew")
			self.frame3.grid(row=0, column=2, sticky="nsew")
			self.frame4.grid(row=0, column=3, sticky="nsew")
			self.frame5.grid(row=0, column=4, sticky="nsew")

		elif frametype == 1:

			tk.Frame.__init__(self, parent, *args, **options)

			self.grid_columnconfigure(0, weight=1, uniform="group1")
			self.grid_rowconfigure(0, weight=1)
			self.aframe = tk.Frame(self)

			self.aframe.grid_columnconfigure(0, weight=1)

			self.aframe.grid_rowconfigure(0, weight=1)
			self.aframe.pack(anchor='center', fill='both', expand='true', padx='500', pady='50')
			# self.aframe.grid(column=0, row=0, padx='500', pady='50', sticky='nwse')

	def frameCreation(self, frametype):
		if frametype == 0:
			return [self.frame1, self.frame2, self.frame3, self.frame4, self.frame5]
		elif frametype == 1:
			return self.aframe

	def deleteFrames(self):
		self.frame1.destroy()
		self.frame2.destroy()
		self.frame3.destroy()
		self.frame4.destroy()
		self.frame5.destroy()


keyboard = Controller()
''' NOTES:
	ToggledFrame class used to create the frames which contains the data shown for each team. Initially made with
	toggles in mind hence the name, but later on revised to just adopt the settings as a better way of user interactivity.
'''


class ToggledFrame(tk.Frame):

	def __init__(self, parent, text="", text2="", *args, **options):
		tk.Frame.__init__(self, parent, *args, **options)

		self.show = tk.IntVar()
		self.show.set(1)

		self.title_frame = ttk.Frame(self)
		self.title_frame.pack(fill="x", expand=1)

		ttk.Label(self.title_frame, text=text, font=('Courier', 12)).pack(side="left", fill="x", expand=1)
		self.currentTeamName = text
		self.currentAttendingName = text2
		# self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='-', command=self.toggle, variable=self.show, style='Toolbutton')
		# self.toggle_button.pack(side="left")

		self.sub_frame = tk.Frame(self, relief="ridge", borderwidth=1, bg='white')
		self.sub_frame.pack(fill="x", expand=1)

	# self.sub_toggle_button = tk.Button(self.sub_frame, text="x", width=1, command=self.delete)
	# self.sub_toggle_button.pack(side= "right")

	# self.sub_auto_button = tk.Button(self.sub_frame, text="%", width=2)
	# self.sub_auto_button.pack(side= "left")

	def toggle(self):
		if bool(self.show.get()):
			self.sub_frame.pack(fill="x", expand=1)
			self.toggle_button.configure(text='-')
		else:
			self.sub_frame.forget()
			self.toggle_button.configure(text='+')

	def delete(self):
		deleteprompt = Popup(self, 1, self.currentTeamName).getBoolean()
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


''' NOTES:
	Popup class used to initiate a user prompt. callinfo variable used to differentiate between which type is being called.
	Example of a way to call this class would be:
	
	deleteprompt = Popup(self, 1, self.currentTeamName).get_boolean()
	
	This will return a 1 if true and 0 if false. The next course of action can then be made depending on the return value
	that the user has given.
'''


class Popup(tk.Toplevel):
	value = 0

	def __init__(self, master, callinfo, teaminfo):
		tk.Toplevel.__init__(self, master)

		x = root.winfo_x()
		y = root.winfo_y()

		w = self.winfo_width()
		h = self.winfo_height()

		dx = (root.winfo_width()/2)
		dy = (root.winfo_height()/2)
		self.resizable(0, 0)

		self.geometry("%dx%d+%d+%d" % (500, 100, x+dx, y+dy))

		if callinfo == 1:
			labeltext1 = 'Are you sure you want to save your current settings?'
			labeltext2 = 'You can return here to edit them again or go to Help>Reset My List to reset to default.'

		elif callinfo == 2:
			labeltext1 = 'Would you like to reset your list?'
			labeltext2 = 'Resetting will bring back all items that you had previously cleared'

		toplabel = tk.Label(self, height=1, font='Helvetica 14', text=labeltext1)
		toplabel.pack()

		warning = tk.Label(self, text=labeltext2)
		warning.pack()

		bottomFrame = Frame(self)
		bottomFrame.pack()
		btn = tk.Button(bottomFrame, text="OK", command=self.deleteFrame)
		btn.pack(side=LEFT)
		btn = tk.Button(bottomFrame, text="CANCEL", command=self.cancelDelete)
		btn.pack(side=LEFT)

		self.transient(root) 	# set to be on top of the main window
		self.grab_set() 		# hijack all commands from the master (clicks on the main window are ignored)
		root.wait_window(self) 	# pause anything on the main window until this one closes (optional)

	def deleteFrame(self):
		self.value = 1
		self.destroy()

	def cancelDelete(self):
		self.value = 0
		self.destroy()

	def getBoolean(self):
		return self.value

# ///////////////////////////////////////////////////////////////////////// Team Initializer
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# colorWords used to check if a color keyword is in the team, then changes the border to reflect.
colorWords = ['Blue', 'Red', 'Aqua', 'Purple', 'Green', 'Yellow']


def endsWith(endvalue):
	# This method is used to check for the legend at the bottom of the charts.
	# Check if current passed in value ends with a number or not
	m = re.search(r'\d+$', endvalue)
	# if the string ends in digits m will be a Match object, or None otherwise.
	if m is not None:
		print(endvalue + ' contains a digit')
		return 1


''' NOTES:
	The TeamList class can be used by calling upon it and passing in a tab for it to loop through.
	Assuming there will be 5 total columns, the TeamList class will loop through each item and
	assign each item a column and row to display to then moving onto the next. 
'''
class TeamList:

	def __init__(self, tab):
		i = 0
		b = 0  # item row
		while i < itemCount:
			if not set(deleteArray).isdisjoint(teamList[i]):
				print('match detected. Skipping current addition')
				i += 1
			else:
				try:
					singleTeam = teamList[i]
				except IndexError:
					singleTeam = teamList[0]

				try:
					# endswith() function used to check if team has a numbered ending, signifying sickcall and removes it.
					if endsWith(singleTeam[date + tab]):
						singleTeam[date+tab] = singleTeam[date+tab][:-1]

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
					teamName = ToggledFrame(currentColumn[b], text=singleTeam[0], text2=singleTeam[date+tab], relief="groove",
											borderwidth=4, bg=setColor)
					teamName.pack(fill="x", pady=2, padx=2, anchor="n")

					entry = ttk.Entry(teamName.sub_frame)
					entry.insert(0, singleTeam[date+tab])
					entry.pack()

					b += 1
					i += 1
				except IndexError:
					break


# ///////////////////////////////////////////////////////////////////////// About and Settings
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


''' NOTES:
	AboutFrame's implementation uses a tk.Text which has inherent support for scrollbars. 
	To use, pass in a link to a text file found online (I used the about text found in the
	github) and it will display the text in it's own frame on screen. 
	
	DisplayText is how the text is deciphered. Once a text file has been passed in, the
	data will be read line by line then printed.
'''
class AboutFrame(tk.Label):
	def __init__(self, parent, url=None):
		self.url = url
		tk.Frame.__init__(self, parent)
		self.textFrame = tk.Frame(parent)
		self.textFrame.pack(fill='both', expand=True)
		self.textFrame.grid_propagate(True)
		self.textFrame.grid_rowconfigure(0, weight=1)
		self.textFrame.grid_columnconfigure(0, weight=1)

		self.text = tk.Text(self.textFrame, borderwidth=3, relief='sunken')
		self.text.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

		self.scrollbar = tk.Scrollbar(self.textFrame, command=self.text.yview)
		self.scrollbar.grid(row=0, column=1, sticky='nsew')
		self.text['yscrollcommand'] = self.scrollbar.set
		data = urllib.request.urlopen(self.url)
		self.dataText = ''
		self.displayText(data)

	def displayText(self, data):

		for line in data:
			self.dataText += line.decode()

		self.text.insert(END, self.dataText)
		self.text.config(font=("Courier", 12), undo=True, wrap='word', state=DISABLED)


''' NOTES:
	Settings is a little bit different than the about frame. SettingsFrame uses a tk.Canvas to 
	implement the scrollbar and will adapt to however long the canvas needs to be based on the
	amount of teams passed in.
	To use, call the class as well as passing in the teams or entries that is needed to be displayed.
	In this case, I passed in all the teams that were detected upon loading.
'''
class SettingsFrame(tk.Label):
	def __init__(self, parent, entries=[]):
		Frame.__init__(self, parent)
		self.vars = []
		self.entries = entries
		self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
		self.frame = tk.Frame(self.canvas, background="#ffffff")
		self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.vsb.set)

		self.vsb.pack(side="right", fill="y")
		self.canvas.pack(side="left", fill="both", expand=True)
		self.canvas.create_window((0,0), window=self.frame, anchor="nw", tags="self.frame")

		self.frame.bind("<Configure>", self.onFrameConfigure)
		self.displayList()

	def displayList(self):
		# Checks each of the items passed in and assigns a checkbox to each. If the item is in delete array,
		# then uncheck said item, otherwise check.
		for entry in self.entries:
			compareString = str(entry)
			var = IntVar()
			checkbox = Checkbutton(self.frame, text= entry, variable= var, font=('Courier', 12), bg='#ffffff') # off by default
			checkbox.pack(anchor= W, expand= True)
			self.vars.append(var)
			if compareString in deleteArray:
				print('displaylist shows same, unselect')
			# Do nothing, off by default
			else:
				checkbox.select()

	def state(self):

		return map((lambda var: var.get()), self.vars)

	def saveState(self, indexes=[]):
		# saveState will call the Popup and prompt user input, and if yes, will save state and restart.
		applyprompt = Popup(self, 1, 0).getBoolean()
		if applyprompt:
			deleteArray=[]
			for index in indexes:
				a = self.entries[index]

				deleteArray.append(a)

			deleteString= ','.join(deleteArray)
			config.set('frames', 'key', deleteString)
			with open('config.ini', 'w') as f:
				config.write(f)

			python = sys.executable
			os.execl(python, python, * sys.argv)

		else:
			print('canceled. do nothing')

	def onFrameConfigure(self, event):

		# Resets the scroll region to that of the items inside.
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

# ///////////////////////////////////////////////////////////////////////// Page initialization
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Creating the tab controller
tabControl = ttk.Notebook(root)          # Create Tab Control

tab0 = ttk.Frame(tabControl)            # Create a tab
tab0.grid_columnconfigure(0, weight=1)
tab0.grid_rowconfigure(0, weight=1)
tab1 = ttk.Frame(tabControl)            # Create a tab
tab1.grid_columnconfigure(0, weight=1)
tab1.grid_rowconfigure(0, weight=1)
tab2 = ttk.Frame(tabControl)            # Create a tab
tab2.grid_columnconfigure(0, weight=1)
tab2.grid_rowconfigure(0, weight=1)

mainframe0 = CreateWindow(tab0, frametype=0)
mainframe0.grid(row=0, column=0, sticky="nsew")
currentColumn = mainframe0.frameCreation(0)
TeamList(0)

mainframe1 = CreateWindow(tab1, frametype=0)
mainframe1.grid(row=0, column=0, sticky="nsew")
currentColumn = mainframe1.frameCreation(0)
TeamList(1)

mainframe2 = CreateWindow(tab2, frametype=0)
mainframe2.grid(row=0, column=0, sticky="nsew")
currentColumn = mainframe2.frameCreation(0)
TeamList(2)

# The text is stored in the date declaration above
tabControl.add(tab0, text=dateVarToday)      # Add the tab
tabControl.add(tab1, text=dateVarTmr)      # Add the tab
tabControl.add(tab2, text=dateVarNext)      # Add the tab
tabControl.grid(row=0, column=0, sticky="nsew")  # Pack to make visible


# //////////// About frame declaration
aboutframe = CreateWindow(root, frametype=1)
aboutframe.grid(row=0, column=0, sticky="nsew")
currentAboutFrame = aboutframe.frameCreation(1)
# URL for the about frame
abouturl = 'https://raw.githubusercontent.com/onionsinmypants/AmionViewer/master/README.txt'

backphoto = PhotoImage(file="back.png")
backbutton = Button(currentAboutFrame, image=backphoto, text="back", command=lambda: raiser(tabControl), relief=FLAT)
backbutton.pack(anchor='nw')

testLabel = AboutFrame(currentAboutFrame, abouturl)
testLabel.pack(side="top", fill="both", expand=True)

# //////////// Settings frame declaration
settingFrame = CreateWindow(root, frametype=1)
settingFrame.grid(row=0, column=0, sticky="nsew")
currentSettingFrame = settingFrame.frameCreation(1)
currentSettingFrame.grid_rowconfigure(0, weight=1)
currentSettingFrame.grid_rowconfigure(1, weight=1)

currentSettingFrame.grid_columnconfigure(0, weight=1)
currentSettingFrame.grid_columnconfigure(1,weight=1)

backbutton2 = Button(currentSettingFrame, image=backphoto, text="back", command=lambda: raiser(tabControl), relief= FLAT)
backbutton2.grid(row=0, column=0, sticky='sw')

applyphoto = PhotoImage(file='apply.png')
Button(currentSettingFrame, text='apply', image=applyphoto, command=lambda: allStates(), relief=FLAT).grid(row=0, column=1, sticky='se')

# Appends 0th element of singleTeam into settingsTeamList to pass into the SettingsFrame.
i = 0
settingsTeamList = []
while i < itemCount:
	try:
		singleTeam = teamList[i]
	except IndexError:
		singleTeam = teamList[0]
	settingsTeamList.append(singleTeam[0])
	i += 1

# SettingsFrame requires an input of an array list of items to display, so we pas in settingsTeamList above.
testLabel2 = SettingsFrame(currentSettingFrame, settingsTeamList)
testLabel2.grid(row=1,column=0, sticky='nsew', columnspan=2)
testLabel2.config(relief=GROOVE, bd=2)


def allStates():
	# rando is the value/index of all items that are unchecked. Pass that into saveState to enter the values into config.

	rando = [i for i, x in enumerate(list(testLabel2.state())) if x == 0]
	print(rando)
	testLabel2.saveState(rando)


raiser(tabControl)

# ///////////////////////////////////////////////////////////////////////// Top menu
# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label='File', menu=filemenu)
filemenu.add_command(label='Exit', command=root.quit)
settingsmenu = Menu(menu)
menu.add_cascade(label='Settings', menu=settingsmenu)
settingsmenu.add_command(label='Teams to Display', command=lambda: raiser(settingFrame))
helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='Reset my List', command=lambda: deletePreferences())
helpmenu.add_separator()
helpmenu.add_command(label='About', command=lambda: raiser(aboutframe))
helpmenu.add_command(label='Check for Updates', command=lambda: raiser(aboutframe))


def deletePreferences():
	deleteprompt = Popup(root, 2, "").getBoolean()
	if deleteprompt:
		print(deleteprompt)
		open("config.ini", "w").close()
		python = sys.executable
		os.execl(python, python, * sys.argv)

	else:
		print(deleteprompt)


root.mainloop()
