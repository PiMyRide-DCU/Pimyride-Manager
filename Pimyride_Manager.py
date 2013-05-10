#!/usr/bin/python

###########################################################################
# PiMyRide_Manager.py
# Version 1.0
# Copyright 2013 Alan Kehoe, David O'Regan (www.pimyride.com)
#
# This file is part of PiMyRide.
#
# PiMyRide is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# PiMyRide is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PiMyRide; if not, visit http://www.gnu.org/licenses/gpl.html
###########################################################################

#--------------------------------------------Imports----------------------

from datetime import datetime
import os
import csv
import webbrowser

import wx.lib.plot as plot
import wx.lib.sheet as sheet
import wx
import wx.grid


#--------------------------------------------Global Variables-------------

ID_BUTTON = 100
ID_EXIT = 200
ID_SPLITTER = 300
new = 2  # open in a new tab, if possible


#--------------------------------------------Tree display(Left Panel)-----
class TreeDisplay(wx.GenericDirCtrl):
    def __init__(self, parent, id):
        wx.GenericDirCtrl.__init__(self, parent, id, style=wx.LC_REPORT)


#--------------------------------------------CSV Display(Right Panel)-----
class MySheet(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.directory = os.getcwd()

    # Open the log file and load the table
    def OnOpen(self, event):
        dlg = wx.FileDialog(self, 'Choose a file',
                            self.directory, '', 'CSV files(*.csv)|*.csv|All files(*.*)|*.*', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.directory = dlg.GetDirectory()
            self.filename = os.path.join(self.directory, dlg.GetFilename())
            self.file = file(self.filename, 'r')

            # Open a file, save path to file
            f = open('path', 'w')
            f.write(self.directory + '/' + dlg.GetFilename())

            # Use the sniffer to ensure its a CSV file
            ensure = csv.Sniffer().sniff(self.file.read(1024))
            self.file.seek(0)
            csvfile = csv.reader(self.file, ensure)

            # Check to see if there is a header in the file
            samplecsv = self.file.read(2048)
            self.file.seek(0)
            if csv.Sniffer().has_header(samplecsv):
                colnames = csvfile.next()
            else:
                row = csvfile.next()
                colnames = []
                for i in range(len(row)):
                    colnames.append('col%d' % i)
                self.file.seek(0)

            if getattr(self, 'grid', 0):
                self.grid.Destroy()
            self.grid = wx.grid.Grid(self, -1)
            self.grid.CreateGrid(0, len(colnames))

        # Use the Boxsizer to re-enlarge the table within the right
        # panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)
        self.SetSizer(sizer)

        # Put the column headings in place
        for i in range(len(colnames)):
            self.grid.SetColLabelValue(i, colnames[i])

        # Now fill the rows & then print them
        rows = 0
        for row in csvfile:
            self.grid.AppendRows(1)
            for i in range(len(row)):
                try:
                    self.grid.SetCellValue(rows, i, row[i])
                except:
                    self.grid.AppendCols(1, True)

            rows += 1
        self.file.close()
        self.grid.AutoSizeColumns(True)
        self.ReSizer()

    def ReSizer(self):
        x, y = self.GetSize()
        self.SetSize((x, y + 1))
        self.SetSize((x, y))


#--------------------------------------------PiMyRide(Main Frame)---------
class PiMyRide(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title)

        # Set splitter for two panels(left,right)
        self.splitter = wx.SplitterWindow(
            self, ID_SPLITTER, style=wx.SP_BORDER)
        self.splitter.SetMinimumPaneSize(100)

        # Actually split the windows(Tree,Panel)
        p1 = TreeDisplay(self.splitter, -1)
        p2 = MySheet(self.splitter)
        p3 = graph(self.splitter, -1, 'Trend')
        self.splitter.SplitVertically(p1, p2)

        # Make the file menu in main frame, open & exit
        filemenu = wx.Menu()
        filemenu.Append(102, "O&pen (ALT + O)", "Open A File")
        filemenu.Append(101, "E&xit (ALT + X)", " Terminate the program")
        filemenu.AppendSeparator()

        # Add help menu
        helpmenu = wx.Menu()
        helpmenu.Append(104, "PiMyRide User Manual")
        helpmenu.Append(106, "PiMyRide Logger Installation")
        helpmenu.Append(107, "PiMyRide Manager Installiation")

        # Make the menu bar in main frame
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(helpmenu, "&Help")

        # Set the menu bar(Top)
        self.SetMenuBar(menuBar)

        # Bind the events to the selected menu options
        self.Bind(wx.EVT_MENU, self.OnExit, id=101)
        self.Bind(wx.EVT_MENU, p2.OnOpen, id=102)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=104)
        self.Bind(wx.EVT_MENU, self.OnLogger, id=106)
        self.Bind(wx.EVT_MENU, self.OnManager, id=107)
        self.Bind(wx.EVT_MENU, self.OnSite, id=108)
        wx.EVT_MENU(self, wx.ID_OPEN, p2.OnOpen)

        # Set the boxsizer for the buttons across the bottom
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        # Make the buttons for the bottom of the frame
        button1 = wx.Button(self, ID_BUTTON + 1, "View Log (ALT + O)")
        button3 = wx.Button(self, ID_BUTTON + 3, "Trend Log (ALT + T)")
        button2 = wx.Button(self, ID_BUTTON + 2, "Visit the WebSite (ALT + W)")
        button4 = wx.Button(self, ID_EXIT, "Quit The Manager (ALT + X)")

        # Add them to screen
        self.sizer2.Add(button1, 1, wx.EXPAND)
        self.sizer2.Add(button3, 1, wx.EXPAND)
        self.sizer2.Add(button2, 1, wx.EXPAND)
        self.sizer2.Add(button4, 1, wx.EXPAND)

        # Bind the events to the buttons on the bottom of the screen
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_BUTTON, self.graphend, id=ID_EXIT)
        self.Bind(wx.EVT_BUTTON, p2.OnOpen, id=ID_BUTTON + 1)
        self.Bind(wx.EVT_BUTTON, p3.OnInit, id=ID_BUTTON + 3)
        self.Bind(wx.EVT_BUTTON, self.OnSite, id=ID_BUTTON + 2)

        #Bind events for keyboard shortcuts
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_ALT, ord('O'), 102),
                                         (wx.ACCEL_ALT, ord('X'), 101),
                                         (wx.ACCEL_ALT, ord('T'), ID_BUTTON + 3),
                                         (wx.ACCEL_ALT, ord('W'), 108)])
        self.SetAcceleratorTable(accel_tbl)

        # Set the sizer for the splitter
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.splitter, 1, wx.EXPAND)
        self.sizer.Add(self.sizer2, 0, wx.EXPAND)
        self.SetSizerAndFit(self.sizer)

        # Display the Application in full screen
        size = wx.DisplaySize()
        self.SetSize(size)

        # Make the status bar
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText(os.getcwd())
        self.Center()
        self.Show(True)

    #--------------------------------------------PiMyRide(Functions)----------


    def OnHelp(self, event):
        help = "http://www.pimyride.com/wp-content/uploads/2013/03/PiMyRide-Manual-1.0.docx"
        webbrowser.open(help, new=new)

    def OnSite(self, event):
        site = "http://www.pimyride.com/"
        webbrowser.open(site, new=new)

    def OnLogger(self, event):
        logger = "http://www.pimyride.com/?page_id=40"
        webbrowser.open(logger, new=new)

    def OnManager(self, event):
        manager = "http://www.pimyride.com/?page_id=96"
        webbrowser.open(manager, new=new)

    def OnExit(self, event):
        self.Close(True)
        event.Skip()

    def graphend(graph, event):
        graph.OnExit
        event.Skip()

        #--------------------------------------------Graph Menu(Trend's)----------


class graph(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(280, 280))

        btn1 = wx.Button(self, 1, 'Speed Vs Fuel Consumption', (70, 50))
        btn2 = wx.Button(self, 2, 'Speed Vs RPM', (70, 80))
        btn4 = wx.Button(self, 4, 'Close', (70, 140))
        wx.EVT_BUTTON(self, 1, self.OnLine1)
        wx.EVT_BUTTON(self, 2, self.OnLine2)
        wx.EVT_BUTTON(self, 4, self.OnQuit)


    #--------------------------------------------Pass the path function-------
    def getpath(self, event):
        config = open('path', 'rb')
        path = config.read()

        #--------------------------------------------CSV reader & Array Creation-----------------------------------------------
        # CSV Reader
        f = open(path, 'rb')
        reader = csv.reader(f)
        reader.next()

        # Variable Declerations
        Avg_RPM = 0.0
        Avg_MPH = 0.0
        Avg_Throttle_Position = 0.0
        Avg_Calculated_Load = 0.0
        Avg_Coolant_Temp = 0.0
        Avg_Air_Temp = 0.0
        Avg_Intake_Manifold_Pressure = 0.0
        Avg_Air_Flow_Rate = 0.0
        Avg_MPG = 0.0

        Count = 0

        # Array Decelerations
        Time = []
        RPM = []
        MPH = []
        Throttle_Position = []
        Calculated_Load = []
        Coolant_Temp = []
        Air_Temp = []
        Intake_Manifold_Pressure = []
        Air_Flow_Rate = []
        MPG = []

        # Populate the Arrays
        for row in reader:
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = row
            Time.append(col1)
            RPM.append(int(float(col2)))
            MPH.append(int(float(col3)))
            Throttle_Position.append(col4)
            Calculated_Load.append(col5)
            Coolant_Temp.append(int(float(col6)))
            Air_Temp.append(int(float(col7)))
            Intake_Manifold_Pressure.append(int(float(col8)))
            Air_Flow_Rate.append(int(float(col9)))
            MPG.append(int(float(col10)))
        f.close()

        # Calculate the trip time in seconds
        start = datetime.strptime(Time[1], '%d%b-%H:%M:%S.%f')
        end = datetime.strptime(Time[len(Time) - 1], '%d%b-%H:%M:%S.%f')

        def time2secs(d):
            return d.day * 24 * 60 * 60 + d.hour * 60 * 60 + d.minute * 60 + d.second

        Trip_Duration = time2secs(end) - time2secs(start)

        for i in range(len(Time) - 1):
            Avg_MPH = Avg_MPH + MPH[i + 1]
            Count = Count + 1

        # Calculate the trip distance
        graph.Trip_Distance = ((Avg_MPH / Count) / 3600.0) * Trip_Duration

        #--------------------------------------------Actual Graph Creation & Functions-----------------------------------------
        # Create the list's of tuples to be used in the graph's
        graph.data1 = zip(MPH, MPG)
        graph.data2 = zip(MPH, RPM)

        # Sort the tuple by Speed
        graph.data1.sort(key=lambda tup: tup[0])


    # First Graph
    def OnLine1(self, child):
        frm = wx.Frame(self, -1, 'Speed Vs Fuel Consumption', size=(600, 450))
        client = plot.PlotCanvas(frm)
        line = plot.PolyLine(graph.data1, legend='', colour='red', width=3)
        gc = plot.PlotGraphics(
            [line], 'Speed Vs Fuel Consumption     Trip Distance: ' + '%.2f' % graph.Trip_Distance, 'Miles Per Hour',
            'Fuel Consumption')
        client.Draw(gc, xAxis=(0, 120), yAxis=(0, 120))
        frm.Show(True)

    # Second Graph
    def OnLine2(self, child):
        frm = wx.Frame(self, -1, 'Speed Vs Engine RPM', size=(600, 450))
        client = plot.PlotCanvas(frm)
        line = plot.PolyLine(graph.data2, legend='', colour='blue', width=3)
        gc = plot.PlotGraphics(
            [line], 'Speed Vs Engine RPM     Trip Distance: ' + '%.2f' % graph.Trip_Distance, 'Miles Per Hour',
            'Engine RPM')
        client.Draw(gc, xAxis=(0, 120), yAxis=(0, 8000))
        frm.Show(True)

    # Quit Function
    def OnQuit(self, event):
        self.Destroy()

    # Initialize project
    def OnInit(self, parent):
        dlg = graph(None, -1, 'Trending Graphs')
        dlg.Show(True)
        dlg.Centre()
        graph.getpath(self, None)
        return True


#--------------------------------------------Program Start & Loop---------
app = wx.App(0)
PiMyRide(None, -1, 'PiMyRide Log Manager')
app.MainLoop()
