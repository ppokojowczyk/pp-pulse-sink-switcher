#!/usr/bin/env python
import Tkinter as tk # for GUI
import subprocess # this is needed for executing shell commands
import re # for getting information from shell commands outputs

class PpPulseSinkSwitcher(tk.Frame):

    class Sink(object):
        display = ""
        id = ""
        default = bool

    def __init__(self, master=None):
        tk.Frame.__init__(self, master) # new main frame
        self.setSinks() # initialize pulseaudio sinks 'collection'
        self.master.config(borderwidth = 10) # set border width for main frame
        self.grid(row = 0, column = 0) # position frame
        self.addSinksFrame() # initialize frame that holds sinks radio buttons
        self.renderSinks() # render radio buttons for sinks
        self.initButtonsFrame() # initialize frame that holds buttons
        self.bindKeys() # set keys bindings

    # create frame that holds sinks radio buttons
    def addSinksFrame(self):
        self.sinksFrame = tk.Frame(self.master) # new frame
        self.sinksFrame.grid(row = 0, pady = 10, sticky='w') # position frame

    # create frame for buttons
    def initButtonsFrame(self):
        self.ButtonsFrame = tk.Frame(self.master) # new frame
        self.ButtonsFrame.grid(row = 1) # position frame
        self.addButtons() # add buttons to frame

    # add buttons
    def addButtons(self):
        self.closeButton = tk.Button(self.ButtonsFrame, text='Close', command=self.quit, underline=0) # add "Close" button
        self.master.bind('<Alt_L><c>', lambda e:self.quit()) # add hotkey
        self.closeButton.grid() # position button

    # create 'collection' of pulseaudio sinks
    def setSinks(self):
        self.sinks = [] # sinks collection
        output = subprocess.check_output(['pactl', 'list', 'sinks']) # use pactl to get informations about sinks
        result = re.split("Sink #.", output) # split sinks data into array
        output = subprocess.check_output(['pactl', 'info']) # use pactl to get information about default sink
        defaultSink = re.findall(".*Default Sink: (.*)", output)[0] # get name of default sink
        result.pop(0) # get rid of first useless element

        # loop through sinks data and create Sink objects
        for str in result:
            name = re.findall(".*Name: (.*)", str)[0] # get name
            description = re.findall(".*Description: (.*)", str)[0] # get description
            sink = self.Sink() # create new sink object
            sink.name = name # name of sink
            sink.description = description # description of sink
            sink.default = defaultSink == name and True or False # check if sink is default
            self.sinks.append(sink) # add sink to sinks 'collection'

    # keys bindings
    def bindKeys(self):
        self.master.bind('<Escape>', lambda e:self.quit()) # press Escape to quit

    # render radio buttons for all sinks
    def renderSinks(self):
        var = tk.IntVar()
        count = 1 # sinks counter
        for sink in self.sinks: # loop through all sinks and render radio button for them
            tk.Radiobutton(self.sinksFrame, text=sink.description + ' (' + sink.name + ')', variable = var, value=count, command=lambda sink=sink: self.changeSink(sink, var)).grid(sticky='w')
            sink.default and var.set(count)
            count = count+1 # increment sinks counter

    # set default sink and redirect all inputs to selected sink
    def changeSink(self, sink, var):
        self.muteAllSinks(); # mute all sinks
        subprocess.check_output(['pacmd', 'set-default-sink', sink.name]) # set default sink by its name
        output = subprocess.check_output(['pacmd', 'list-sink-inputs']) # get information about all inputs
        inputsIndices = re.findall(".*index: (.*)", output) # put all inputs indices into array
        for index in inputsIndices: # loop through all inputs and send them to selected sink
            subprocess.check_output(['pacmd', 'move-sink-input', index, sink.name])
        subprocess.check_output(['pactl', 'set-sink-mute', sink.name, '0']) # unmute selected sink

    # mute all sinks
    def muteAllSinks(self):
        for sink in self.sinks: # loop through all sinks
            subprocess.check_output(['pactl', 'set-sink-mute', sink.name, '1']) # mute sink

sinkSwitcher = PpPulseSinkSwitcher() # new instance
sinkSwitcher.master.title('Pulse Sink & Input Switcher') # set title
sinkSwitcher.mainloop() # run application

# that's all folks
