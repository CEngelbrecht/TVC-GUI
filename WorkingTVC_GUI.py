import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from matplotlib import style
import Tkinter as Tk	
import random 
import threading
import Queue
import time
import socket
import numpy as np
import random

#some initial stylistic choices
matplotlib.use("TkAgg")
style.use("ggplot") 		
FONT = ("Helvetica", 12)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

The GUI Part of Things

'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class GuiPart(Tk.Tk):

	def __init__(self,master,textqueue,graphqueue, endCommand):
		
		self.textQueue = textqueue
		self.graphQueue = graphqueue
		
		#Extensive __init__ to set up buttons, grid locations, subplots, etc. Considering putting this in a seperate file.
		
		#Placed in dictionary, for ease of future changes. 
		gridDict = {	'byeButton':		[0,0],		#[row,column]
						'GreetButton':		[0,1],
						'CurrentXLabel':	[1,0],
						'CurrentXDisplay':	[1,1],
						'CurrentYLabel':	[2,0],
						'CurrentYDisplay':	[2,1],
						'XSetPointLabel':	[3,0],
						'XEntry':			[3,1],
						'YSetPointLabel':	[4,0],
						'YEntry':			[4,1],
						'RoutineList':		[5,0],
						'RoutineButton':	[5,1]
					}
		
		bye_button = Tk.Button(master,text = 'Goodbye', command = endCommand, font = FONT)
		bye_button.grid(row = gridDict['byeButton'][0], column = gridDict['byeButton'][1])

		greet_button = Tk.Button(master, text="Greet", command=self.printStuff,font = FONT)
		greet_button.grid(row = gridDict["GreetButton"][0], column = gridDict["GreetButton"][1])

		xEntryVar = Tk.StringVar()  # Need to initialize a StringVar
		xEntry = Tk.Entry(master, textvariable=xEntryVar)
		xEntry.grid(row = gridDict['XEntry'][0], column = gridDict['XEntry'][1])

		xSendButton = Tk.Button(master, text = 'Set X Set Point',command = lambda:self.dataSend(xEntryVar.get()),font = FONT)
		xSendButton.grid(row = gridDict['XSetPointLabel'][0], column = gridDict['XSetPointLabel'][1])   

		self.currentXVar = Tk.StringVar()
		currentXDisplay = Tk.Label(master,textvariable = self.currentXVar,font = FONT)
		currentXDisplay.grid(row = gridDict['CurrentXDisplay'][0], column = gridDict['CurrentXDisplay'][1])
			
		currentXLabel = Tk.Label(master, text = "Current X Location",font = FONT)
		currentXLabel.grid(row = gridDict["CurrentXLabel"][0], column = gridDict["CurrentXLabel"][1])
			
		yEntryVar = Tk.StringVar()  # Need to initialize a StringVar
		yEntry = Tk.Entry(master, textvariable=yEntryVar)
		yEntry.grid(row = gridDict['YEntry'][0], column = gridDict['YEntry'][1])
		      	
		ySendButton = Tk.Button(master, text = 'Set Y Set Point',command = lambda:self.dataSend(yEntryVar.get()),font = FONT)
		ySendButton.grid(row = gridDict['YSetPointLabel'][0], column = gridDict['YSetPointLabel'][1])
			
		self.currentYVar = Tk.StringVar()
		currentYLabel = Tk.Label(master,textvariable = self.currentYVar,font = FONT)
		currentYLabel.grid(row = gridDict["CurrentYDisplay"][0], column = gridDict["CurrentYDisplay"][1]) 
			
		currentYDisplay = Tk.Label(master, text = "Current Y Location",font = FONT)
		currentYDisplay.grid(row = gridDict["CurrentYLabel"][0], column = gridDict["CurrentYLabel"][1])
			
			
		routineList = ["Routine 1","Routine 2"]
		routineVar= Tk.StringVar()
		routineVar.set(routineList[0]) # default choice
		routineMenu = Tk.OptionMenu(master, routineVar, *routineList)
		routineMenu.grid(row = gridDict['RoutineList'][0],column = gridDict['RoutineList'][1])
			
		routineButton = Tk.Button(master,text = "Dance for Me",command = lambda:self.routineSend(routineVar.get()),font = FONT)
		routineButton.grid(row = gridDict["RoutineButton"][0],column = gridDict["RoutineButton"][1])

		#Below is the setup for all the subplots.
		self.canvasFig = plt.figure(1)
		fig = Figure(figsize=(5, 5), dpi=100)
		self.figSubPlot1 = fig.add_subplot(211)
		self.figSubPlot2 = fig.add_subplot(212)
		x = [0] #initialize plots to zero. 
		y = [0]
		fig.subplots_adjust(hspace = 0.5)
		self.line1, = self.figSubPlot1.plot(x,y)
		self.line2, = self.figSubPlot2.plot(x,y)
		self.canvas = FigureCanvasTkAgg(fig, master=master)
		
		ax1 = self.canvas.figure.axes[0]
		ax1.set_title("Polar Plot of current Angle",fontsize = 12)
		ax1.set_xlim(-6.5,6.5)
		ax1.set_ylim(-6.5,6.5)
		ax2 = self.canvas.figure.axes[1]
		ax2.set_xlim(-6.5,6.5)
		ax2.set_ylim(-6.5,6.5)
		ax2.set_title('Negative Polar Plot of Current Angle',fontsize = 12)
		
		self.canvas.show()
		self.canvas.get_tk_widget().grid(row = 6 ,column = 0, columnspan = 2, sticky = 'S')

	def routineSend(self,routineNumber):
		#This will send command eventually to perform a routine
		pass
		
	def printStuff(self):
		#Just checking if this button works
		pass

	def processIncomingText(self,msg):
		
		self.currentXVar.set(round(msg,5))
		self.currentYVar.set(round(msg,5)) #Updates the X and Y Current Position Labels

	def processIncomingGraph(self,data):

		angle = data
		
		#Currently this just draws a line that goes in a circle, assumung updatePlot passes 
		#information in such as the angle of the system. 
		r = 5
		
		x = r * np.cos(angle)
		y = r * np.sin(angle)
		
		self.line1.set_data([0,x],[0,y])
		self.line2.set_data([0,-x],[0,-y])
		 
		self.canvas.draw()

	def dataSend(self,message):
		
		#Send information to Pi. This should probably be happening in ThreadedClient
		datasendsock.sendto(message,(piIP,sendport))
		
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

The Thread Handler and I/O Part of Things

'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ThreadedClient:

	def __init__(self, master):

		self.master = master
	
		self.textQueue = Queue.Queue()
		self.graphQueue = Queue.Queue()
		
		self.gui = GuiPart(master, self.textQueue, self.graphQueue, self.endApplication)

		self.running = True
		self.textThread = threading.Thread(target=self.getInfo)
		self.graphThread = threading.Thread(target = self.getInfo)

		self.textThread.start()
		self.graphThread.start()

		self.periodicCallText() #Starts periodic calls to update the text labels and graphs
		self.periodicCallGraph()

	def getInfo(self):
		
		while self.running:

			#msg = datagetsock.recvfrom(8)[0] #8 because that's the number of bytes the server sends about angle info
			msg = random.random() 
			self.textQueue.put(msg)
			self.graphQueue.put(msg)

	def periodicCallText(self):

		msg = self.textQueue.get(1) #Takes first object out of Queue, updates, calls every 10ms
		self.gui.processIncomingText(msg)

		self.master.after(10, self.periodicCallText)

	def periodicCallGraph(self):

		x = [] #reinitialize to an empty list every time.

		for i in range(10):
			x.append(self.graphQueue.get(0))
		
		data = sum(x)/len(x) # computes average of 10 inputs based on timed call in 'after'

		self.gui.processIncomingGraph(data)

		self.master.after(100,self.periodicCallGraph)

	def endApplication(self):

		self.running = False
		import sys
		root.destroy()
		sys.exit(1)
		
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''

The Function Calling and Network Setup Part of Things. 

'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

piIP = "10.42.0.208"
#datagetsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
getport = 6969
#datagetsock.bind(('',getport)) #Client needs to bind to socket, server doesn't 

#datasendsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sendport = 12345


		
root = Tk.Tk()
GUI = ThreadedClient(root)
root.mainloop()

