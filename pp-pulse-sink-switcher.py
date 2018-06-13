#!/usr/bin/env python
import Tkinter as tk
import subprocess
import re

class Application(tk.Frame):

    class Sink(object):
        display = ""
        id = ""
        default = bool

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.setSinks()
        self.master.config(borderwidth = 10)
        self.grid(row = 0, column = 0)
        self.addSinksFrame()
        self.renderSinks()
        self.initButtonsFrame()

    def addSinksFrame(self):
        self.sinksFrame = tk.Frame(self.master)
        self.sinksFrame.grid(row = 0, pady = 10, sticky='w')

    def initButtonsFrame(self):
        self.ButtonsFrame = tk.Frame(self.master)
        self.ButtonsFrame.grid(row = 1)
        self.addButtons()

    def addButtons(self):
        self.closeButton = tk.Button(self.ButtonsFrame, text='Close', command=self.quit, underline=0)
        self.master.bind('<Alt_L><c>', lambda e:self.quit())
        self.closeButton.grid()

    def setSinks(self):
        self.sinks = []
        output = subprocess.check_output(['pactl', 'list', 'sinks'])
        result = re.split("Sink #.", output)

        output = subprocess.check_output(['pactl', 'info'])
        defaultSink = re.findall(".*Default Sink: (.*)", output)[0]

        result.pop(0)
        for str in result:
            name = re.findall(".*Name: (.*)", str)[0]
            description = re.findall(".*Description: (.*)", str)[0]
            sink = self.Sink()
            sink.name = name
            sink.description = description
            sink.default = defaultSink == name and True or False
            self.sinks.append(sink)

    def renderSinks(self):
        var = tk.IntVar()
        count = 1
        for sink in self.sinks:
            tk.Radiobutton(self.sinksFrame, text=sink.description + ' (' + sink.name + ')', variable = var, value=count, command=lambda sink=sink: self.changeSink(sink, var)).grid(sticky='w')
            sink.default and var.set(count)
            count = count+1

    def changeSink(self, sink, var):
        subprocess.check_output(['pacmd', 'set-default-sink', sink.name])
        output = subprocess.check_output(['pacmd', 'list-sink-inputs'])
        inputsIndexes = re.findall(".*index: (.*)", output)
        for index in inputsIndexes:
            subprocess.check_output(['pacmd', 'move-sink-input', index, sink.name])

sinkSwitcher = Application()
sinkSwitcher.master.title('Pulse Sink & Input Switcher')
sinkSwitcher.mainloop()
