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
		stats = [str(self.runs),str(self.balls),str(self.strikeRate)]
		for i in range(3):
			txt[i].delete(0,END)
			txt[i].insert(INSERT,stats[i])

	def modifyBowlStats(self,txt):
		overs = str(int(self.balls/6))
		balls = str(int(self.balls % 6))
		stats1 = overs + "." + balls
		stats = [stats1, str(self.runs),str(self.wickets),str(self.economy)]
		for i in range(4):
			txt[i].delete(0,END)
			txt[i].insert(INSERT,stats[i])
	def writeBatStats(self,stats,player,aCode,i):
		stats['cricStats'][player][1] += self.runs
		stats['cricStats'][player][2] += self.balls
		if (int(stats['cricStats'][player][2]) != 0):
			stats['cricStats'][player][3] = float(format(float(stats['cricStats'][player][1]*100.0)/stats['cricStats'][player][2],fL))
		else:
			stats['cricStats'][player][3] = 0
		
		stats['cricStats'][player][8] = float(format(float(stats['cricStats'][player][1]) * (float(stats['cricStats'][player][3])/100),fL))
		
		lenVal = len(stats['BatArchives'])-(2-int(i/2))
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
		lenVal = len(stats['BowlArchives'])-1
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
		self.batsmanNames = []
		self.bowlerNames = []
	
	def updatePlayerNames(self,listVal1,listVal2):
		self.batsmanNames = listVal1
		self.bowlerNames = listVal2

	def getBatsmenNames(self):
		return self.batsmanNames

	def getBowlerNames(self):
		return self.bowlerNames

	def writeStats(self,data,namesDict,batsmanNames,bowlerNames):
		modifyUniDict(data,'BatArchives',3)
		for i in range(4):
			currName = self.batsmanNames[i%2]
			data = self.batStats[int(i/2)][i%2].writeBatStats(data,namesDict[currName],uniDict[currName],i)
		modifyUniDict(data,'BowlArchives',4)
		for i in range(2):
			currName = self.bowlerNames[i]
			data = self.bowlStats[i].writeBowlStats(data,namesDict[currName],uniDict[currName])
		for j in range(4):
			i = j+1
			data['cricStats'][i][10] = data['cricStats'][i][8] + data['cricStats'][i][9]
		
		return data
	
	def modifyStats(self,inngNo,maxOvers,oversText,scoreText,batStats,bowlStats):
		oversText.delete('1.0',END)
		overs = str(int(self.balls/6))
		balls = str(self.balls%6)
		oversText.insert(INSERT,overs + "." + balls)
		scoreText.delete('1.0',END)
		scoreText.insert(INSERT,str(self.score) + "/" + str(self.wickets))	
		for i in range(4):
			self.batStats[int(i/2)][i%2].modifyBatStats(batStats[i])
		for i in range(2):
			self.bowlStats[i].modifyBowlStats(bowlStats[i])
		if (self.wickets == 4 or self.balls == maxOvers*6):
			return inngNo+1
		else:
			return inngNo

	def getCurrentOverEntries(self):
		copyOfEntries = self.listOfEntries[:]
		balls = self.balls % 6
		currEntries = " | "
		if len(copyOfEntries) == 0:
			return ""
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
		self.inningsCount = 0
		self.possOvers = [4,6,8,10,12,14]
		width = self.window.winfo_screenwidth()
		height = self.window.winfo_screenheight()
		self.window.title("Cricket Saga")
		self.window.geometry(str(width) + "x" + str(height))
		self.bg_colour = 'cornsilk2'
		self.fg_colour = 'navy'
		self.window['bg'] = self.bg_colour
		self.currFile = file1
		self.oldFile = file2
		
		lbl = Label(self.window, text = "Welcome to", bg = self.bg_colour, fg = self.fg_colour, font = ('timesnewroman 30 bold'))
		lbl.grid(column = 0,row = 0,padx = 75,pady = 100)
		
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

		lbl = Label(self.window, text = "No of Overs", bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
		lbl.grid(column = 1,row = 4,)
		
		self.txt = ttk.Combobox(self.window,width = 10)
		self.txt['values'] = self.possOvers
		self.txt.current(4)
		self.txt.grid(column=2, row=4,pady = 5)

		self.selected = IntVar()
		self.selected.set(1)
		lbl = Label(self.window, text = "Mode of Match", bg = self.bg_colour, fg = self.fg_colour,font = ("Arial",self.subTitleSize))
		lbl.grid(column = 1,row = 5) 
		self.modes = ['T20','Test']
		colors = ['black','black']
		for i in range(2):
			rad1 = Radiobutton(self.window,text=self.modes[i], fg=colors[i], bg = self.bg_colour,value=i, variable=self.selected)
			rad1.grid(column=i+2, row=5,pady = 5)

		startMatch = Button(self.window, text="Start Match", bg = 'navy', fg = 'yellow', font = 'timesnewroman 14 bold italic', command=self.clickedStartMatch)
		startMatch.grid(column = 2,columnspan = 2,row = 6,pady = 7)

		lbl = Label(self.window, text = "Cricket Saga!!!", bg = self.bg_colour, fg = self.fg_colour, font = 'timesnewroman 30 bold italic')
		lbl.grid(column = 4,row = 7,padx = 125,pady = 100)

		self.window.mainloop()

	def clickedStartMatch(self,var = True):
		self.scoreText = []
		self.oversText = []
		self.batsmanNames = []
		self.bowlerNames = []
		self.batsmanStats = []
		self.bowlerStats = []
		self.innings = []	
		self.teams = [[],[]]
		self.currInn = 0
		self.inningsCount = 0
		for i in range(self.noOfInnings):
			self.innings.append(Innings())

		for i in range(4):
			self.teams[i%2].append(self.playerNames[i].get())
		
		print(self.teams)
		self.overs = int(self.txt.get())
		
		if var:
			self.lead = 0
			title = ""
			if self.selected.get() == 0:
				print("T20")
				title = "Match"
				self.inningsCount = 1
			elif self.selected.get() == 1:
				print("Test")
				title = "Innings-1"
			self.window1 = Toplevel()
			self.window1.title(title)
			self.window1.geometry('1350x1200')
			self.runsButtons(10,self.window1)
			self.window1.mainloop()
			
	
	def showStatsFun(self,innVal):
		print(innVal,end = "innVal\n")
		val = self.reqRowVal
		window = self.currentRunningWindow
		lblCol = [0,2]
		lblTexts = ["Score","Overs"]
		
		inn = innVal	
		rowCol = val+2
		
		for i in range(2):
			lbl = Label(window, text = lblTexts[i],bg = self.bg_colour,fg = self.fg_colour, font = ("Arial",self.subTitleSize))
			lbl.grid(column = lblCol[i],row = rowCol,pady = 4)
		
		self.scoreText.grid(column = lblCol[0]+1,row = rowCol)
		self.scoreText.delete('1.0',END)
		self.scoreText.insert(INSERT,"0")
		self.oversText.grid(column = lblCol[1]+1,row = rowCol)
		self.oversText.delete('1.0',END)
		self.oversText.insert(INSERT,"0.0")
		
		texts = ["Batsman","Runs","Balls","StrikeRate"]
		for j in range(4):
			lbl = Label(window, text = texts[j], bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
			lbl.grid(column = j+1,row = val+5,padx = 3)
		lbl = Label(window, text = "Innings"+str(inn+1),bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize),padx = 25)
		lbl.grid(column = 0,row = val+6)
		
		texts = ["Bowler","Overs","Runs","wickets","Economy"]
		for j in range(5):
			lbl = Label(window, text = texts[j], bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
			lbl.grid(column = j+6,row = val+5,padx = 2)
			
		batsmanNames = self.innings[inn].getBatsmenNames()
		bowlerNames = self.innings[inn].getBowlerNames()
		print(batsmanNames,end = "batsmanNames\n")
		print(bowlerNames,end = "bowlerNames\n")
		for i in range(4):
			self.batsmanNames[i]['values'] = (batsmanNames[0],batsmanNames[1])
			self.batsmanNames[i].current(i%2) #set the selected item
			for j in range(3):
				self.batsmanStats[i][j].delete(0,END)
				self.batsmanStats[i][j].insert(INSERT,"0")
				self.batsmanStats[i][j].configure({"background" : self.bg_colour})
				self.batsmanStats[i][j].configure({"foreground" : self.fg_colour})
		
		for i in range(2):
			self.bowlerNames[i]['values'] = (bowlerNames[0],bowlerNames[1])
			self.bowlerNames[i].current(i%2) #set the selected item
			for j in range(4):
				self.bowlerStats[i][j].delete(0,END)
				self.bowlerStats[i][j].configure({"foreground" : self.fg_colour})
				self.bowlerStats[i][j].configure({"background" : self.bg_colour})
				self.bowlerStats[i][j].insert(INSERT,"0")

	def runsButtons(self,val,window):
		self.reqRowVal = val
		self.currentRunningWindow = window
		self.bg_colour = 'SlateGray2'
		self.fg_colour = 'black'
		window['bg'] = self.bg_colour		

		lbl = Label(window, text = "Runs", bg = self.bg_colour, fg = self.fg_colour, font = ("Arial",self.subTitleSize))
		lbl.grid(column = 0,row = val)

		runsbgColour = ['ivory2','SkyBlue2','MistyRose2','plum2']
		runsfgColour = ['black','black','black','black']
		runsTexts = ["0","1","2","4"]
		runsCommands = [lambda:self.addScoreFunction(0),lambda:self.addScoreFunction(1),lambda:self.addScoreFunction(2),lambda:self.addScoreFunction(4)]
		runsWidthVal = 7
		runsHeightVal = 3
		bottomTexts = ["Wicket","Undo","Wide","NoBall"]
		bottombg = ['red','LemonChiffon3','DarkOrange1','DarkOrange1']
		bottomfg = ['white','black','white','white']
		bottomCommands = [lambda:self.addScoreFunction('Wicket'),lambda:self.addScoreFunction('IE'),lambda:self.addScoreFunction('Wide'),lambda:self.addScoreFunction('Wide')]
		bottomHeight = 3
		
		for i in range(4):
			btn = Button(window, text=runsTexts[i],bg = runsbgColour[i],font = 'Arial 15 bold',fg = runsfgColour[i],command=runsCommands[i],width = runsWidthVal,height = runsHeightVal)
			btn.grid(column = i+1,row = val,pady = 10,padx = 5)
		
		for i in range(4):	
			btn = Button(window, text=bottomTexts[i], bg = bottombg[i],fg = bottomfg[i],font = 'Arial 15 bold',command=bottomCommands[i],height = bottomHeight,width = runsWidthVal)
			btn.grid(column = i+1,row = val+1,pady = 5)

		self.scoreText = Text(window,width = 5,height = 1)
		self.oversText = Text(window,width = 5,height = 1)
		self.currInnStats = [StringVar(),StringVar()]
		self.currInnVals = ["0/0 0.0","0.0"]
		self.currOverStats = StringVar()
		self.leadOrTrail = StringVar()
		self.currOverStats.set("Curr Over : ")
		self.leadOrTrail.set("")

		inn = 0
		for i in range(4):
			combo = ttk.Combobox(window,width = 10)
			combo['values']= (self.teams[inn][0],self.teams[inn][1])
			combo.current(i%2) #set the selected item
			combo.grid(column=1, row=val+i+6,pady = 2)
			self.batsmanNames.append(combo)
			tempList = []
			for j in [2,3,4]:
				txt = Entry(window,width=10)
				txt.grid(column=j, row=val+i+6)
				txt.insert(INSERT,"0")
				txt.configure({"background" : self.bg_colour})
				txt.configure({"foreground" : self.fg_colour})
				tempList.append(txt)
			self.batsmanStats.append(tempList)
		
		for i in range(2):
			combo = ttk.Combobox(window,width =10)
			combo['values']= (self.teams[1-inn][0],self.teams[1-inn][1])
			combo.current(1 - i%2) #set the selected item
			combo.grid(column=6, row=val+i+6,padx = 3,pady = 2)
			self.bowlerNames.append(combo)
			tempList = []
			for j in [2,3,4,5]:
				txt = Entry(window,width=10)
				txt.grid(column=j+5, row=val+i+6,padx = 3)
				txt.configure({"foreground" : self.fg_colour})
				txt.configure({"background" : self.bg_colour})
				txt.insert(INSERT,"0")
				tempList.append(txt)
			self.bowlerStats.append(tempList)

		batsmenList = []
		bowlerList = []
		for i in range(2):
			batCombo = self.batsmanNames[i]
			bowlCombo = self.bowlerNames[i]
			batsmenList.append(batCombo.get())
			bowlerList.append(bowlCombo.get())
		list1 = bowlerList[:]
		list2 = batsmenList[:]
		list1.reverse()
		list2.reverse()
		self.innings[0].updatePlayerNames(batsmenList,bowlerList)
		self.innings[1].updatePlayerNames(list1,list2)
		self.showStatsFun(0)

		colvals = [6,9]
		colSpanVals = [5,2]
		padyVals = [5,5]
		for i in range(1):
			self.currInnStats[i].set(self.currInnVals[i])
			lbl = Label(window, textvariable = self.currInnStats[i], bg = self.bg_colour, fg = 'gray1', font = 'Arial 120 bold')
			lbl.grid(column = colvals[i],row = val,rowspan = 3,columnspan = colSpanVals[i],pady = padyVals[i])
		
		lbl = Label(window, textvariable = self.currOverStats, bg = self.bg_colour, fg = 'gray1', font = 'Arial 20 bold',anchor = 'w')
		lbl.grid(column = 6,row = val+2,columnspan = 5,pady = 5)

		lbl = Label(window, textvariable = self.leadOrTrail, bg = self.bg_colour, fg = 'gray1', font = 'Arial 20 bold')
		lbl.grid(column = 6,row = val*2+2,columnspan = 5,pady = 5)

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

	def setOrder(self):
		batsmenList = self.innings[self.currInn].getBatsmenNames()
		bowlerList = self.innings[self.currInn].getBowlerNames()
		# for inn in range(2):
		if self.batsmanNames[0].get() == batsmenList[1]:
			batsmenList.reverse()
			for i in range(4):
				self.batsmanNames[i]['values'] = (batsmenList[0],batsmenList[1])
				self.batsmanNames[i].current(i%2) #set the selected item
		if self.bowlerNames[0].get() == bowlerList[1]:
			bowlerList.reverse()
			for i in range(2):
				self.bowlerNames[i]['values'] = (bowlerList[0],bowlerList[1])
				self.bowlerNames[i].current(i%2) #set the selected item
		
		self.innings[self.currInn].updatePlayerNames(batsmenList,bowlerList)
	
	def displayModifiedStats(self):
		oldInnVal = self.currInn
		self.currInn = self.innings[self.currInn].modifyStats(self.currInn,self.overs,self.oversText,self.scoreText,self.batsmanStats,self.bowlerStats)
		self.currInn = min(self.currInn,self.noOfInnings-1)
		self.currInnStats[0].set(self.scoreText.get('1.0','1.5') + " " + self.oversText.get('1.0','1.4'))
		self.currOverStats.set("Curr Over : " + self.innings[oldInnVal].getCurrentOverEntries())
		if self.currInn == 0:
			scoreDiff = self.innings[self.currInn].retScore() - self.innings[1-self.currInn].retScore() + self.lead
			if scoreDiff < 0:
				self.leadOrTrail.set("Trail by " + str(abs(scoreDiff)))
			elif scoreDiff == 0:
				self.leadOrTrail.set("Scores level")
			else :
				self.leadOrTrail.set("Lead by " + str(scoreDiff))	
		elif self.currInn == 1 and self.inningsCount == 0:
			if self.innings[1].retWickets() == 4:
				self.endMatch()
			scoreDiff = self.innings[self.currInn].retScore() - self.innings[1-self.currInn].retScore() - self.lead
			if scoreDiff < 0:
				self.leadOrTrail.set("Trail by " + str(abs(scoreDiff)))
			elif scoreDiff == 0:
				self.leadOrTrail.set("Scores level")
			else:
				self.leadOrTrail.set("Lead by " + str(scoreDiff))
		else:
			scoreDiff = self.innings[self.currInn].retScore() - self.innings[1-self.currInn].retScore() - self.lead
			if self.innings[1].retWickets() == 4:
				self.leadOrTrail.set(self.teams[0][0] + " and " + self.teams[0][1] + " won the match by " + str(abs(scoreDiff)-1) + " runs")
				self.endMatch()				
			if scoreDiff < 0:
				self.leadOrTrail.set("Need " + str(abs(scoreDiff)) + " more runs to win")
			elif scoreDiff == 0:
				self.leadOrTrail.set("Scores level")
			else:
				self.leadOrTrail.set(self.teams[1][0] + " and " + self.teams[1][1] + " won the match by " + str(4 - self.innings[self.currInn].retWickets()) + " wickets")
				self.endMatch()

		if self.currInn == 1:
			if self.innings[1].retBalls() == 0:
				self.showStatsFun(0)
				self.innings[0].modifyStats(self.currInn,self.overs,self.oversText,self.scoreText,self.batsmanStats,self.bowlerStats)
				self.currInnStats[0].set(self.scoreText.get('1.0','1.5') + " " + self.oversText.get('1.0','1.4'))
				self.currOverStats.set("Curr Over : " + self.innings[0].getCurrentOverEntries())
			elif self.innings[1].retBalls() == 1:
				self.showStatsFun(1)
				self.innings[1].modifyStats(self.currInn,self.overs,self.oversText,self.scoreText,self.batsmanStats,self.bowlerStats)

	def addScoreFunction(self,val):
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
			result = False
			while not(result) and self.currInn >= 0:
				result = self.innings[self.currInn].incorrectEntry()
				if (not(result)):
					self.currInn -= 1
			self.currInn = max(self.currInn,0)
			self.showStatsFun(self.currInn)

		elif val == 'Wicket':
			self.innings[self.currInn].addWicket()

		self.displayModifiedStats()
				
	def saveStats(self):
		data = get_data(self.currFile)
		save_data(self.oldFile,data)
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
		save_data(self.currFile,data)
		saveData = messagebox.showinfo("Stats Info","Stats saved succesfully!!!!")
		self.lead = self.innings[0].retScore() - self.innings[1].retScore()
		if self.selected.get() == 1 and self.inningsCount == 0:
			self.window2 = Toplevel()
			self.window2.title("Innings-2")
			self.window2.geometry('1350x1200')
			self.clickedStartMatch(False)
			self.runsButtons(17,self.window2)
			self.inningsCount += 1
			self.window2.mainloop()
		self.window2.destroy()
		self.window1.destroy()

	def endMatch(self):
		result = messagebox.askyesno("Cricket Saga","Are you sure you want to end the Innings?")
		if (result):
			self.saveStats()
	
	def endDay(self):
		result = messagebox.askyesno("Cricket Saga","Are you sure you want to end the Day?")
		if (result):
			self.saveStats()
		os.system("start excel " + self.currFile)
		self.window.destroy()
	
	def copyData(self):
		save_data(self.currFile,get_data(self.oldFile))	
	
	def quitWindow(self):
		self.window1.destroy()

match = Match("C:/Users/chait/Desktop/cricketFever/cricStats.xlsx","C:/Users/chait/Desktop/cricketFever/oldCricStats.xlsx")	
# match = Match("cricStats.xlsx","oldCricStats.xlsx")	