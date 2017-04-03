#!/bin/env/python3

import serial
import sys
import glob
import re
from tkinter import *

#Elizabeth Adelaide, March 2017
#Comissioned by Robin Cameron
#Python GUI for interfacing with arduino system using serial communication
#Full code and documentation can be found here: https://github.com/elizabethadelaide/robinProjectorControl

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
       # ports.extend(glob.glob('/dev/pts/*')) #for virtual ports
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':
    print(serial_ports())

ports= serial_ports() #detect serial ports
for x in range(len(ports)):
	print(ports[x] + " " + str(x))



class PortChoose(Frame): #initial select port GUI
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.grid()

		self.portLabel = Label(master, text="Choose port")
		self.portLabel.grid(column=0, row=1)

		self.portButton = [0 for x in range(len(ports))]
		for x in range(len(ports)):
			self.portButton[x] = Button(master, command = lambda x=x: self.selectPort(x), text=ports[x]);
			self.portButton[x].grid(column=x+1, row=1)

	def selectPort(self, x):
		try:
			global ser
			ser = serial.Serial(ports[x])
			print("Connected to port " + ports[x])
			self.portButton[x].configure(bg="green")
			self.quit()
		except serial.SerialException:
			print("port unavaible")
			self.portButton[x].configure(bg="red")
				

class GUI(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.grid()

		self.TitleLabel = Label(master, text="Projector Control")
		self.TitleLabel.grid(column=0, row=0)

		self.cascadeLabel = Label(master, text="Cascade Time (s)")
		self.cascadeLabel.grid(column=0, row=3)

		self.cascadeEntry = Entry(master)
		self.cascadeEntry.grid(column=1, row=3)
		self.cascadeEntry.insert(END, "1")

		self.cycleLabel = Label(master, text="Cycle Time (s)")
		self.cycleLabel.grid(column=2, row=3)

		self.cycleEntry = Entry(master)
		self.cycleEntry.grid(column=3, row=3)
		self.cycleEntry.insert(END, "21")

		self.cascadeButton = Button(master, command=self.cascadeClick, text="Submit")
		self.cascadeButton.grid(column=6, row=3)


		self.stopButton = Button(master, command = self.stopClick, text="Stop")
		self.stopButton.grid(column=0, row=4) 		

		self.resumeButton = Button(master, command = self.resumeClick, text="Resume")
		self.resumeButton.grid(column=2, row=4)
		
		self.pauseButton = Button(master, command = self.pauseClick, text="Pause")
		self.pauseButton.grid(column=1, row=4) 		
		
		self.advancedButton = Button(master, command = self.advancedClick, text="Additional Options")
		self.advancedButton.grid(column=1, row=5)
		self.advancedBool = 1
		self.advancedButton.configure(bg="gray")
		
		self.clickLabel = Label(master, text="Click Time(s)")
		
		self.clickEntry = Entry(master)
		self.clickEntry.insert(END,"0.5")
		

		self.stopButton.configure(bg="gray")
		self.pauseButton.configure(bg="gray")
		self.resumeButton.configure(bg="gray")

		self.ProjNum= [0 for x in range(7)]
		for x in range(7):
			self.ProjNum[x] = Button(master, command= lambda x=x: self.selectProj(x), text=x+1)
			self.ProjNum[x].grid(column=x, row=2)


	def cascadeClick(self):

		casc = "0" + self.cascadeEntry.get()
		cycle = "0" + self.cycleEntry.get()
		click = "0" + self.clickEntry.get()

		p = re.compile('\d*\.?\d+\Z') #reg expression to match float
	
		if (p.match(casc)!=None and p.match(cycle)!=None and p.match(click)!=None):
			cascnum = (int)(1000.0*float(casc)) #convert to ms
			cyclenum = (int)(1000.0*float(cycle))
			clicktime = (int)(1000.0* float(click))

			#check to make sure it is doable
			if (cyclenum < clicktime*7):
				cyclenum = clicktime*7
				self.cycleEntry.config(textvariastr(cyclenum))
			if (cyclenum < cascnum*7):
				cyclenum = cascnum*7
				self.cycleEntry.config(textvariable=str(cyclenum))
	
			ser.write(b'13') #code for changing time
			num = cascnum.to_bytes(4, byteorder='big')
			
			ser.write(num)
			
			num = cyclenum.to_bytes(4, byteorder='big')		
			ser.write(num)
			ser.write(b'\n')

			print("Submitted")
			self.cascadeButton.configure(bg="green")

		else:
			self.cascadeButton.configure(bg="red")
			
			
	def resumeClick(self):
		print("Resume")
		ser.write(b'12')
		ser.write(b'\n')
		self.stopButton.configure(bg="gray")
		self.pauseButton.configure(bg="gray")
		self.resumeButton.configure(bg="green")
	def stopClick(self):
		print("Stop")
		ser.write(b'10')
		ser.write(b'\n')
		self.stopButton.configure(bg="red")
		self.pauseButton.configure(bg="gray")
		self.resumeButton.configure(bg="gray")
	def pauseClick(self):
		print("Pause")
		ser.write(b'11')
		ser.write(b'\n')
		self.stopButton.configure(bg="gray")
		self.pauseButton.configure(bg="red")
		self.resumeButton.configure(bg="gray")
	def selectProj(self,x):
		print("Proj " + str(x))
		num = ("%02d" % x).encode()
		ser.write(num)
		ser.write(b'\n')
	def advancedClick(self):
		if (self.advancedBool):
			self.advancedButton.configure(bg="green")
			self.clickEntry.grid(column=2, row=6)
			self.clickLabel.grid(column=1, row=6)
			self.advancedBool=0
		else:
			self.advancedButton.configure(bg="gray")
			self.clickLabel.grid_forget()
			self.clickEntry.grid_forget()
			self.advancedBool=1
			

portFrame = PortChoose()

portFrame.mainloop()

guiFrame = GUI()

while True:
	line = ""
	if (ser.in_waiting):
		try:
			line = ser.readline().decode("utf-8")
			reg = re.compile('[0123456789]') #only read numbers from serial 
			number = ''.join(list(filter(reg.search, line))); #get number from serial
			
			if (number.isdigit()):
				number = int(number)
				for i in range(0, 7):
					if (number == i):
						guiFrame.ProjNum[i].configure(bg="red")
					else:
						guiFrame.ProjNum[i].configure(bg="gray")

			
		except serial.SerialException:
			print("Arduino temporarily not available")
	
	#if (number !=''):
	#	print(number)
	


	guiFrame.update_idletasks()
	guiFrame.update()

		



