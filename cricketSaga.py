from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from pandas_ods_reader import read_ods
from pyexcel_xlsx import get_data
from pyexcel_xlsx import save_data
import os
fL = '.2f'
uniDict = {'DJ' : 0,'DC' : 1,'HK' : 2,'MS' : 3}
def modifyUniDict(data,archiveName,length):
	namesList = data[archiveName][0]
	for i in range(4):
		uniDict[namesList[i*length]] = i
	print(uniDict)
class IndStats():
	def __init__(self):
		self.runs = 0
		self.balls = 0
		self.strikeRate = 0
		self.economy = 0
		self.wickets = 0
	def redoScore(self,val):
		self.runs -= val
		self.balls -= 1
		if (self.balls != 0):
			self.strikeRate = format(float((self.runs)*100.0)/self.balls,fL)
			self.economy = format(float((self.runs)*6.0)/self.balls,fL)
		else :
			self.strikeRate = 0
			self.economy = 0
	
	def addScore(self,val):
		self.runs += val
		self.balls += 1
		if (self.balls != 0):
			self.strikeRate = format(float((self.runs)*100.0)/self.balls,fL)
			self.economy = format(float((self.runs)*6.0)/self.balls,fL)
		else:
			self.strikeRate = 0
			self.economy = 0
	
	def addWicket(self,val):
		self.wickets += val
		self.balls += val
		if (self.balls != 0):
			self.economy = format(float((self.runs)*6.0)/self.balls,fL)
	
	def addWide(self,val):
		self.runs += val
		if (self.balls != 0):
			self.economy = format(float((self.runs)*6.0)/self.balls,fL)
	
	def retScore(self):
		return self.runs
	
	def retBalls(self):
		return self.balls

	def retBalls2(self):
		overs = str(int(self.balls/6))
		balls = str(int(self.balls % 6))
		return overs + "." + balls
	
	def retSR(self):
		return self.strikeRate
	
	def retEconomy(self):
		return self.economy

	def retWickets(self):
		return self.wickets
	
	def modifyBatStats(self,txt):
		# print(txt)
		# format(self.strikeRate,'.2f')
		# format(self.strikeRate,'.2f')
		stats = [str(self.runs),str(self.balls),str(self.strikeRate)]
		for i in range(3):
			txt[i].delete(0,END)
			txt[i].insert(INSERT,stats[i])
			# txt[i].config(text = stats[i])

	def modifyBowlStats(self,txt):
		# format(self.economy,'.2f')
		# format(self.strikeRate,'.2f')
		overs = str(int(self.balls/6))
		balls = str(int(self.balls % 6))
		stats1 = overs + "." + balls
		stats = [stats1, str(self.runs),str(self.wickets),str(self.economy)]
		for i in range(4):
			txt[i].delete(0,END)
			txt[i].insert(INSERT,stats[i])
			# txt[i].config(text = stats[i])
	def writeBatStats(self,stats,player,aCode,i):
		stats['cricStats'][player][1] += self.runs
		stats['cricStats'][player][2] += self.balls
		# print(int(stats['cricStats'][player][2]))
		if (int(stats['cricStats'][player][2]) != 0):
			stats['cricStats'][player][3] = float(format(float(stats['cricStats'][player][1]*100.0)/stats['cricStats'][player][2],fL))
		else:
			stats['cricStats'][player][3] = 0
		
		stats['cricStats'][player][8] = float(format(float(stats['cricStats'][player][1]) * (float(stats['cricStats'][player][3])/100),fL))
		
		lenVal = len(stats['BatArchives'])-(2-int(i/2))
		# player -= 1
		# print('playerVal',end = " ")
		# print(player)
		stats['BatArchives'][lenVal][aCode*3] = self.runs
		stats['BatArchives'][lenVal][aCode*3 + 1] = self.balls
		stats['BatArchives'][lenVal][aCode*3 + 2] = self.strikeRate
		return stats
	
	def getOvers(self,overs,balls):
		overs = str(float(overs))
		a = overs.split(".")
		balls = int(a[0])*6 + int(a[1]) + balls
		return str(int(balls/6)) + "." + str(balls%6)		
	
	def getBalls(self,overs):
		overs = str(float(overs))
		a = overs.split(".")
		balls = int(a[0])*6 + int(a[1])
		return balls
	
	def getEconomy(self,overs,runs):
		balls = self.getBalls(overs)
		if balls != 0:
			return format((float(runs*6.0)/balls),fL)
		else :
			return 0
	
	def writeBowlStats(self,stats,player,aCode):
		stats['cricStats'][player][5] += self.runs
		stats['cricStats'][player][6] += self.wickets
		stats['cricStats'][player][4] = self.getOvers(stats['cricStats'][player][4],self.balls)		
		stats['cricStats'][player][7] = self.getEconomy(stats['cricStats'][player][4],stats['cricStats'][player][5])
		if stats['cricStats'][player][5] != 0:
			stats['cricStats'][player][9] = float(format(float(stats['cricStats'][player][6]) * 6 * (float(self.getBalls(stats['cricStats'][player][4]))/stats['cricStats'][player][5]),fL))
		else :
			stats['cricStats'][player][9] = 4
		# print(player,end = " ")
		# print(stats['cricStats'][player][8],end = " ")	
		# print(stats['cricStats'][player][9],end = " ")	
		lenVal = len(stats['BowlArchives'])-1
		# print(player)
		# player -= 1
		stats['BowlArchives'][lenVal][aCode*4] = str(int((self.balls)/6)) + "." + str((self.balls)%6)
		stats['BowlArchives'][lenVal][aCode*4 + 1] = self.runs
		stats['BowlArchives'][lenVal][aCode*4 + 2] = self.wickets
		stats['BowlArchives'][lenVal][aCode*4 + 3] = self.economy
		return stats

class Innings():
	def __init__(self):
		self.score = 0
		self.balls = 0
		self.wickets = 0
		self.listOfEntries = []
		self.currBatsman = 0
		self.currBowler = 0
		self.batStats = [[IndStats(),IndStats()],[IndStats(),IndStats()]]
		self.bowlStats = [IndStats(),IndStats()]
	
	def writeStats(self,data,namesDict,batsmanNames,bowlerNames):
		# len2 = len(data['BowlArchives'][0])
		# el = []
		# for i in range(len2):
		# 	el.append('')
		# data['BowlArchives'].append(el)
		print(namesDict,end = "namesDict")
		modifyUniDict(data,'BatArchives',3)
		for i in range(4):
			currName = batsmanNames[i].get()
			# print(currName)
			# print(uniDict[currName])
			data = self.batStats[int(i/2)][i%2].writeBatStats(data,namesDict[currName],uniDict[currName],i)
		modifyUniDict(data,'BowlArchives',4)
		for i in range(2):
			currName = bowlerNames[i].get()
			print(currName)
			print(uniDict[currName])
			data = self.bowlStats[i].writeBowlStats(data,namesDict[currName],uniDict[currName])
		for j in range(4):
			i = j+1
			data['cricStats'][i][10] = data['cricStats'][i][8] + data['cricStats'][i][9]
		
		return data
	
	def modifyStats(self,inngNo,maxOvers,oversText,scoreText,batStats,bowlStats):
		oversText[inngNo].delete('1.0',END)
		overs = str(int(self.balls/6))
		balls = str(self.balls%6)
		oversText[inngNo].insert(INSERT,overs + "." + balls)
		scoreText[inngNo].delete('1.0',END)
		scoreText[inngNo].insert(INSERT,str(self.score) + "/" + str(self.wickets))	
		# self.batsmanStats[wickets][0].delete(0,END)
		# print(currBalls,end = "")
		# print(currBowler)
		for i in range(4):
			self.batStats[int(i/2)][i%2].modifyBatStats(batStats[inngNo][i])
		for i in range(2):
			self.bowlStats[i].modifyBowlStats(bowlStats[inngNo][i])
		# print(self.balls,end = " ")
		# print(maxOvers*6)
		print(inngNo,end = " : ")
		print(self.listOfEntries)	
		if (self.wickets == 4 or self.balls == maxOvers*6):
			return inngNo+1
		else:
			return inngNo
		# for i in range(3):
		# 	self.batsmanStats[wickets][i].delete(0,END)
		# 	self.batsmanStats[wickets][i].insert(INSERT,str(batStats[i]))
		
		# for i in range(4):
		# 	self.bowlerStats[currBowler][i].delete(0,END)
		# 	# print(bowlStats[i])
		# 	self.bowlerStats[currBowler][i].insert(INSERT,str(bowlStats[i]))

	def getCurrentOverEntries(self):
		copyOfEntries = self.listOfEntries[:]
		balls = self.balls % 6
		currEntries = " | "
		lastEntry = copyOfEntries[-1]
		if balls == 0 and lastEntry == 'wn':
			while lastEntry == 'wn':
				lastEntry = copyOfEntries.pop()
				if lastEntry == 'wn':
					currEntries = " | " + str(lastEntry) + currEntries
		else :
			if balls == 0:
				balls = 6
			for i in range(balls):
				lastEntry = 'wn'
				while lastEntry == 'wn' and len(copyOfEntries) > 0:
					lastEntry = copyOfEntries.pop()
					currEntries = " | " + str(lastEntry) + currEntries
			if len(copyOfEntries) > 0:
				lastEntry = copyOfEntries[-1]
				while lastEntry == 'wn' and len(copyOfEntries) > 0:
					lastEntry = copyOfEntries.pop()
					if lastEntry == 'wn':
						currEntries = " | " + str(lastEntry) + currEntries
		return currEntries
	
	def retScore(self):
		return self.score

	def retBalls(self):
		return self.balls

	def retWickets(self):
		return self.wickets
	
	def retBatStats(self):
		currBatsStats = self.batStats[int((self.wickets)/2)][self.currBatsman]
		return [currBatsStats.retScore(),currBatsStats.retBalls(),currBatsStats.retSR()]

	def retBowlStats(self):
		currBowlStats = self.bowlStats[self.currBowler]
		return [currBowlStats.retBalls2(),currBowlStats.retScore(),currBowlStats.retWickets(),currBowlStats.retEconomy()]		
	
	def updateCurrBatsmanAndBowler(self):
		currBalls = self.balls
		overs = int(currBalls/6)
		if (currBalls % 6 != 0):
			self.currBowler = (overs % 2)
		# print(self.currBowler,end = " ")
		# print(currBalls,end = " ")
		# print(self.score)
		self.currBatsman = (self.wickets) % 2	
		
	def retCurrBowler(self):
		return self.currBowler

	def addWide(self):
		self.score += 1
		self.listOfEntries.append('wn')
		currBalls = self.balls
		overs = int(currBalls/6)
		self.currBowler = (overs % 2)
		self.bowlStats[self.currBowler].addWide(1)	

	def incorrectEntry(self):
		# print(self.listOfEntries)
		if (len(self.listOfEntries) == 0):
			return False
		lastEntry = self.listOfEntries.pop()
		if (lastEntry == 'w'):
			self.wickets -= 1
		elif (lastEntry == 'wn'):
			self.score -= 1
			self.balls += 1
		else :
			self.score -= int(lastEntry)
		self.balls -= 1		
		self.updateCurrBatsmanAndBowler()
		if (lastEntry == 'w'):
			self.batStats[int((self.wickets)/2)][self.currBatsman].redoScore(0)
			self.bowlStats[self.currBowler].addWicket(-1)	
		elif (lastEntry == 'wn'):
			self.bowlStats[self.currBowler].addWide(-1)	
		else :
			self.batStats[int((self.wickets)/2)][self.currBatsman].redoScore(lastEntry)
			self.bowlStats[self.currBowler].redoScore(lastEntry)
		# print(self.listOfEntries)
		# print(self.balls[self.currInn])
		return True
	def addWicket(self):
		if (self.wickets < 4):
			self.balls += 1
			self.updateCurrBatsmanAndBowler()
			self.bowlStats[self.currBowler].addWicket(1)	
			self.batStats[int((self.wickets)/2)][self.currBatsman].addScore(0)
			self.wickets += 1
			self.listOfEntries.append('w')
			self.updateCurrBatsmanAndBowler()
			if (self.wickets == 4):
				return "Innings Over"
		# if (self.currInn == 2):
		# 	return "Match Over"

	def addScore(self,val):
		self.score += val
		self.balls += 1
		self.updateCurrBatsmanAndBowler()		
		self.batStats[int((self.wickets)/2)][self.currBatsman].addScore(val)
		self.bowlStats[self.currBowler].addScore(val)
		self.listOfEntries.append(val)

class Match():
	def __init__(self,file1,file2):
		self.titleSize = 20
		self.subTitleSize = 15
		self.names = ['DJ','DC','HK','MS']
		self.noOfInnings = 2
		self.currInn = 0
		self.teams = []
		self.overs = 10
		self.window = Tk()
		# myimage = PhotoImage(file = "cric1.gif")
		width = self.window.winfo_screenwidth()
		height = self.window.winfo_screenheight()
		print(width)
		print(height)
		self.window.title("Cricket Saga")
		self.window.geometry(str(width) + "x" + str(height))
		# self.window.geometry('2000x2000')
		self.bg_colour = 'navy'
		self.fg_colour = 'azure'
		self.window['bg'] = self.bg_colour
		self.currFile = file1
		self.oldFile = file2
		# self.window['image'] = img

		#path = "cric1.gif"
		#image = Image.open(path)
		# image.show()
		#print(image.size)
		#print((width,height))
		#new_image = image.resize((width,height))
		#print(new_image.size)
		#photo = ImageTk.PhotoImage(new_image)
		# lbl = Label(self.window, fg = 'white',image = photo,text = "Sample",font = ("Arial",self.subTitleSize))
		# lbl.grid(column = 0,row = 0)
		# lbl.image = photo
		# self.canvas = Canvas(self.window,width = 1350,height = 1200)
		# self.canvas.grid(row = 0,column = 0)
		# self.canvas.create_image(0,0,image=photo,anchor = 'nw')
		lbl = Label(self.window, text = "Welcome to", bg = self.bg_colour, fg = self.fg_colour, font = ('timesnewroman 30 bold'))
		lbl.grid(column = 0,row = 0,padx = 75,pady = 100)
		# lbl = Label(self.window, text = "to", bg = self.bg_colour, fg = self.fg_colour, font = ('Arial 30 bold'))
		# lbl.grid(column = 1,row = 0,padx = 10,pady = 10)
		# lbl = Label(self.window, text = "Cricket", bg = self.bg_colour, fg = self.fg_colour, font = ('Arial 30 bold'))
		# lbl.grid(column = 2,row = 0,padx = 10,pady = 10)
		# lbl = Label(self.window, text = "Saga", bg = self.bg_colour, fg = self.fg_colour, font = ('Arial 30 bold'))
		# lbl.grid(column = 3,row = 0,padx = 10,pady = 10)
		self.playerNames = []
		for i in range(4):
			combo = ttk.Combobox(self.window,width = 15)
			combo['values']= (self.names)
			combo.current(i) #set the selected item
			combo.grid(column=2+(i%2), row=int(i/2)+2,padx = 3,pady = 3)
			self.playerNames.append(combo)
			
		for i in range(2):
			lbl = Label(self.window, text = "Team" + str(1 + i%2), bg = self.bg_colour ,fg = self.fg_colour,font = ("Arial",self.subTitleSize))
			lbl.grid(column = i+2,row = 1)
			# self.labelList.append(lbl)

		lbl = Label(self.window, text = "No of Overs", bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
		lbl.grid(column = 1,row = 4,)
		self.txt = Entry(self.window,width=10)
		self.txt.insert(0,"10")
		self.txt.grid(column=2, row=4,pady = 5)

		self.selected = IntVar()
		lbl = Label(self.window, text = "Mode of Match", bg = self.bg_colour, fg = self.fg_colour,font = ("Arial",self.subTitleSize))
		lbl.grid(column = 1,row = 5) 
		self.modes = ['T20','Test']
		colors = ['red','white']
		for i in range(2):
			rad1 = Radiobutton(self.window,text=self.modes[i], fg=colors[i], bg = self.bg_colour,value=i, variable=self.selected)
			rad1.grid(column=i+2, row=5,pady = 5)
		# btn.grid(column=4, row=1)

		startMatch = Button(self.window, text="Start Match", bg = 'DarkOrange1', fg = 'brown4', font = 'timesnewroman 14 bold italic', command=self.clickedStartMatch)
		startMatch.grid(column = 2,columnspan = 2,row = 6,pady = 7)

		lbl = Label(self.window, text = "Cricket Saga!!!", bg = self.bg_colour, fg = self.fg_colour, font = 'timesnewroman 30 bold italic')
		lbl.grid(column = 4,row = 7,padx = 125,pady = 100)

		self.window.mainloop()

	def clickedStartMatch(self):
		if (self.selected.get() == 1):
			self.noOfInnings = 4
		self.scoreText = []
		self.oversText = []
		self.batsmanNames = []
		self.bowlerNames = []
		self.batsmanStats = []
		self.bowlerStats = []
		self.innings = []	
		self.teams = [[],[]]
		self.currInn = 0
		for i in range(self.noOfInnings):
			self.batsmanNames.append([])
			self.bowlerNames.append([])
			self.batsmanStats.append([])
			self.bowlerStats.append([])
			self.innings.append(Innings())

		# for inn in range(self.noOfInnings):
		for i in range(4):
			self.teams[i%2].append(self.playerNames[i].get())
		
		print(self.teams)
		self.overs = int(self.txt.get())
		
		self.window1 = Toplevel()
		self.window1.title("Match")
		self.window1.geometry('1350x1200')
		self.runsButtons(17,self.window1)
		self.window1.mainloop()
	
	def runsButtons(self,val,window):
		# self.btns = []
		# for i in [0,1,2,4]:
		self.bg_colour = 'SlateGray2'
		self.fg_colour = 'black'
		window['bg'] = self.bg_colour		
		lbl = Label(window, text = "Runs", bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
		lbl.grid(column = 0,row = val)
		# self.image0 = PhotoImage(file = "download.gif")
		runsbgColour = ['ivory2','SkyBlue2','MistyRose2','plum2']
		runsfgColour = ['black','black','black','black']
		runsTexts = ["0","1","2","4"]
		runsCommands = [lambda:self.runsFunction(0),lambda:self.runsFunction(1),lambda:self.runsFunction(2),lambda:self.runsFunction(4)]
		runsWidthVal = 7
		runsHeightVal = 3
		bottomTexts = ["Wicket","Undo","Wide","NoBall"]
		bottombg = ['red','LemonChiffon3','DarkOrange1','DarkOrange1']
		bottomfg = ['white','black','white','white']
		bottomCommands = [lambda:self.runsFunction('Wicket'),lambda:self.runsFunction('IE'),lambda:self.runsFunction('Wide'),lambda:self.runsFunction('Wide')]
		bottomHeight = 3
		
		for i in range(4):
			btn = Button(window, text=runsTexts[i],bg = runsbgColour[i],font = 'Arial 15 bold',fg = runsfgColour[i],command=runsCommands[i],width = runsWidthVal,height = runsHeightVal)
			btn.grid(column = i+1,row = val,pady = 10,padx = 5)
		
		for i in range(4):	
			btn = Button(window, text=bottomTexts[i], bg = bottombg[i],fg = bottomfg[i],font = 'Arial 15 bold',command=bottomCommands[i],height = bottomHeight,width = runsWidthVal)
			btn.grid(column = i+1,row = val+1,pady = 5)

		self.currInnStats = [StringVar(),StringVar()]
		self.currInnVals = ["0/0 0.0","0.0"]
		self.currOverStats = StringVar()
		self.leadOrTrail = StringVar()
		self.currOverStats.set("Curr Over : ")
		self.leadOrTrail.set("")
		# self.statsLbls = []
		colvals = [6,9]
		colSpanVals = [5,2]
		padyVals = [5,5]
		for i in range(1):
			self.currInnStats[i].set(self.currInnVals[i])
			lbl = Label(window, textvariable = self.currInnStats[i], bg = self.bg_colour, fg = 'gray1', font = 'Arial 120 bold')
			lbl.grid(column = colvals[i],row = val,rowspan = 3,columnspan = colSpanVals[i],pady = padyVals[i])
		
		# self.oversLbl = Label(window, textvariable = self.currInnOvers	, bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
		# self.oversLbl.grid(column = 9,row = val,rowspan = 3,columnspan = 2)
		
		lblCol = [0,2]
		lblTexts = ["Score","Overs"]
		
		lbl = Label(window, textvariable = self.currOverStats, bg = self.bg_colour, fg = 'gray1', font = 'Arial 20 bold')
		lbl.grid(column = 6,row = val+2,columnspan = 5,pady = 5)

		lbl = Label(window, textvariable = self.leadOrTrail, bg = self.bg_colour, fg = 'gray1', font = 'Arial 20 bold')
		lbl.grid(column = 6,row = val*2+2,columnspan = 5,pady = 5)

		for inn in range(self.noOfInnings):
			self.scoreText.append(Text(window,width = 5,height = 1))
			self.oversText.append(Text(window,width = 5,height = 1))
			
			rowCol = val*(inn+1)+2
			
			for i in range(2):
				lbl = Label(window, text = lblTexts[i],bg = self.bg_colour,fg = self.fg_colour, font = ("Arial",self.subTitleSize))
				lbl.grid(column = lblCol[i],row = rowCol,pady = 4)
			
			self.scoreText[inn].grid(column = lblCol[0]+1,row = rowCol)
			self.scoreText[inn].insert(INSERT,"0")
			self.oversText[inn].grid(column = lblCol[1]+1,row = rowCol)
			self.oversText[inn].insert(INSERT,"0.0")
			
			texts = ["Batsman","Runs","Balls","StrikeRate"]
			for j in range(4):
				lbl = Label(window, text = texts[j], bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
				lbl.grid(column = j+1,row = val*(inn+1)+5,padx = 3)
			lbl = Label(window, text = "Innings"+str(inn+1),bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize),padx = 25)
			lbl.grid(column = 0,row = val*(inn+1)+6)
			
			for i in range(4):
				combo = ttk.Combobox(window,width = 10)
				combo['values']= (self.teams[0][0],self.teams[0][1])
				combo.current(i%2) #set the selected item
				combo.grid(column=1, row=val*(inn+1)+i+6,pady = 2)
				self.batsmanNames[inn].append(combo)
				tempList = []
				for j in [2,3,4]:
					txt = Entry(window,width=10)
					txt.grid(column=j, row=val*(inn+1)+i+6)
					txt.insert(INSERT,"0")
					txt.configure({"background" : self.bg_colour})
					txt.configure({"foreground" : self.fg_colour})
					tempList.append(txt)
				self.batsmanStats[inn].append(tempList)
			
			texts = ["Bowler","Overs","Runs","wickets","Economy"]
			for j in range(5):
				lbl = Label(window, text = texts[j], bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
				lbl.grid(column = j+6,row = val*(inn+1)+5,padx = 2)
			for i in range(2):
				combo = ttk.Combobox(window,width = 10)
				combo['values']= (self.teams[1][0],self.teams[1][1])
				combo.current(1 - i%2) #set the selected item
				combo.grid(column=6, row=val*(inn+1)+i+6,padx = 3,pady = 2)
				self.bowlerNames[inn].append(combo)
				tempList = []
				for j in [2,3,4,5]:
					txt = Entry(window,width=10)
					txt.grid(column=j+5, row=val*(inn+1)+i+6,padx = 3)
					txt.configure({"foreground" : self.fg_colour})
					txt.configure({"background" : self.bg_colour})
					txt.insert(INSERT,"0")
					tempList.append(txt)
				self.bowlerStats[inn].append(tempList)

			self.teams.reverse()
		
		texts = ["Confirm Order","End Match","End Day","Undo Changes","Close Window"]
		colVals = [1,5,10,10,5]
		rowVals = [val*(self.noOfInnings + 3),val*(self.noOfInnings + 3),val*(self.noOfInnings + 3),val*(self.noOfInnings + 3),val*(self.noOfInnings + 3)+1]
		commands = [self.setOrder,self.endMatch,self.endDay,self.copyData,self.quitWindow]
		padyVals = [50,50,50,50,0]
		bgs = ['DarkOrange1','DarkOrange1','DarkOrange1']
		fgs = ['white','white','white']
		for i in range(len(texts)-2):
			btn = Button(window, text=texts[i], command=commands[i], bg = bgs[i],fg = fgs[i],pady = 15,font = 'Arial 12 bold')
			btn.grid(column = colVals[i],row = rowVals[i],pady = padyVals[i])

		# endMatch = Button(window, text=, command=)
		# endMatch.grid(column = 5,row = )
	
		# redoData = Button(window, text=, command=)
		# redoData.grid(column = 100,row = )

	def setOrder(self):
		for inn in range(2):
			if self.batsmanNames[inn][0].get() == self.teams[0][1]:
				# self.batsmanNames[inn]
				for i in range(4):
					self.batsmanNames[inn][i].current((i+1)%2) #set the selected item
			else:
				for i in range(4):
					self.batsmanNames[inn][i].current(i%2) #set the selected item
			if self.bowlerNames[inn][0].get() == self.teams[1][1]:
				# self.teams[1].reverse()
				for i in range(2):
					self.bowlerNames[inn][i].current((i+1)%2) #set the selected item
			else:
				for i in range(2):
					self.bowlerNames[inn][i].current(i%2) #set the selected item
			self.teams.reverse()
			
	def runsFunction(self,val):
		# print(val)
		if val == 0:
			self.innings[self.currInn].addScore(0)
		elif val == 1:
			self.innings[self.currInn].addScore(1)
		elif val == 2:
			self.innings[self.currInn].addScore(2)			
		elif val == 4:
			self.innings[self.currInn].addScore(4)
		elif val == 'Wide':
			self.innings[self.currInn].addWide()
		elif val == 'IE':
			# currInnVal = self.currInn
			# print(currInnVal)
			result = False
			while not(result) and self.currInn >= 0:
				result = self.innings[self.currInn].incorrectEntry()
				if (not(result)):
					self.currInn -= 1
				#print(result)
				#print(self.currInn)
			# if (!result) 
			if (self.currInn < 0):
				self.currInn = 0
		elif val == 'Wicket':
			self.innings[self.currInn].addWicket()

		oldInnVal = self.currInn
		self.currInn = self.innings[self.currInn].modifyStats(self.currInn,self.overs,self.oversText,self.scoreText,self.batsmanStats,self.bowlerStats)
		self.currInn = min(self.currInn,self.noOfInnings-1)
		self.currInnStats[0].set(self.scoreText[oldInnVal].get('1.0','1.5') + " " + self.oversText[oldInnVal].get('1.0','1.4'))
		self.currOverStats.set("Curr Over : " + self.innings[self.currInn].getCurrentOverEntries())
		# if (self.currInn == 1):
		scoreDiff = self.innings[self.currInn].retScore() - self.innings[1-self.currInn].retScore()
		if scoreDiff < 0:
			self.leadOrTrail.set("Trail by " + str(abs(scoreDiff)))
		elif scoreDiff == 0:
			self.leadOrTrail.set("Scores level")
		else :
			self.leadOrTrail.set("Lead by " + str(scoreDiff))
			# self.currInnStats[1].set(self.oversText[oldInnVal].get('1.0','1.4'))
	def endMatch(self):
		result = messagebox.askyesno("Cricket Saga","Are you sure you want to end the Innings?")
		print(result)	
		if (result):
			# fileName = "cricStats.ods"
			data = get_data(self.currFile)
			save_data(self.oldFile,data)
			# stats = data['cricStats']
			# oldStats = stats
			# save_data(fileName,data)
			# print(data['oldCricStats'])
			namesDict = {}
			for i in range(1,5):
				namesDict[data['cricStats'][i][0]] = i
			strings = ['BatArchives','BatArchives','BowlArchives']
			for i in range(len(strings)):
				len1 = len(data[strings[i]][0])
				el = []
				for j in range(len1):
					el.append('')
				data[strings[i]].append(el)
			for i in range(self.noOfInnings):
				data = self.innings[i].writeStats(data,namesDict,self.batsmanNames[i],self.bowlerNames[i])
				# self.teams.reverse
			# print(stats)
			# data['oldCricStats'] = data['cricStats']
			# data['cricStats'] = stats
			# data['oldCricStats'] = oldStats
			# print(data['oldCricStats'])
			save_data(self.currFile,data)
			saveData = messagebox.showinfo("Stats Info","Stats saved succesfully!!!!")
			print("Data saved succesfully")
			print(saveData)
			if (saveData):
				self.window1.destroy()
			# self.window.destroy()
	def endDay(self):
		self.endMatch()
		os.system("start excel " + self.currFile)
		self.window.destroy()
	def copyData(self):
		save_data(self.currFile,get_data(self.oldFile))	
	def quitWindow(self):
		self.window1.destroy()

#print("Starting")
match = Match("C:/Users/chait/Desktop/cricketFever/cricStats.xlsx","C:/Users/chait/Desktop/cricketFever/oldCricStats.xlsx")	