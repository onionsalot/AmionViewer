import tkinter as tk
from tkinter import ttk
from tkinter import *
from bs4 import BeautifulSoup
import calendar
import datetime
import time
from robobrowser import RoboBrowser
from pynput import mouse
from pynput.keyboard import Key, Controller
from configparser import ConfigParser

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

		self.sub_toggle_button = tk.Button(self.sub_frame, text="x", width=2, command=self.delete)
		self.sub_toggle_button.pack(side= "right")

		self.sub_auto_button = tk.Button(self.sub_frame, text="%", width=2, command=self.clicked)
		self.sub_auto_button.pack(side= "left")

	def toggle(self):
		if bool(self.show.get()):
			self.sub_frame.pack(fill="x", expand=1)
			self.toggle_button.configure(text='-')
		else:
			self.sub_frame.forget()
			self.toggle_button.configure(text='+')

	def delete(self):
		self.sub_frame.forget()
		self.title_frame.forget()
		self.destroy()
		deleteArray.append(self.currentTeamName)
		deleteString= ','.join(deleteArray)
		config.set('frames', 'key', deleteString)
		with open('config.ini', 'w') as f:
			config.write(f)

	def clicked(self):
		print('listener start!')

		def on_click(x, y, button, pressed):
			# Delay
			time.sleep(1)
			print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
			# Press and release space. If EPIC's layout changes, make the necessary changes here;
			keyboard.type('Inpatient')
			keyboard.press(Key.enter)
			keyboard.release(Key.enter)
			keyboard.type(self.currentTeamName)
			keyboard.press(Key.enter)
			keyboard.release(Key.enter)
			keyboard.press(Key.enter)
			keyboard.release(Key.enter)
			keyboard.press(Key.enter)
			keyboard.release(Key.enter)
			keyboard.type(self.currentAttendingName)
			keyboard.press(Key.enter)
			keyboard.release(Key.enter)
			keyboard.type(self.currentAttendingName)
			return False

			if not pressed:
				# Stop listener
				return False

		# Collect events until released
		with mouse.Listener(on_click=on_click) as listener:
			listener.join()


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
# ////////////////////////////// Frame setup


def raiser(frame):
	print('test')
	frame.tkraise()


mainframe = tk.Frame(root)
mainframe.grid(row=0, column=0, sticky="nsew")

aboutframe = tk.Frame(root, bg="blue")
aboutframe.grid(row=0, column=0, sticky="nsew")

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



# Create a label
i = 0
b = 0
currentColumn = [frame1, frame2, frame3, frame4, frame5]
colorWords = ['Blue', 'Red', 'Aqua', 'Purple', 'Green', 'Yellow']

while i < itemCount:
	if not set(deleteArray).isdisjoint(teamList[i]):
		print('match detected. Skipping current addition')
		i += 1
	else:
		try:
			singleTeam = teamList[i]
		except IndexError:
			singleTeam = teamList[0]
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


# ////////////////////////////// Top menu
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
helpmenu.add_command(label='About', command=lambda: raiser(aboutframe))
raiser(mainframe)
root.mainloop()
