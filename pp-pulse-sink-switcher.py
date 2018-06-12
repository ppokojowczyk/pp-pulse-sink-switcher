#!/usr/bin/env python
import Tkinter as tk
import subprocess
import re

class Application(tk.Frame):

    class Sink(object):
        display = ""
        id = ""

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.setSinks()
        self.master.config(borderwidth = 10);
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
        output = subprocess.check_output(['pactl', 'list', 'sinks']);
        result = re.split("Sink #.", output);
        result.pop(0)
        for str in result:
            name = re.findall(".*Name: (.*)", str)[0]
            description = re.findall(".*Description: (.*)", str)[0]
            sink1 = self.Sink()
            sink1.name = name
            sink1.description = description
            self.sinks.append(sink1)

    def renderSinks(self):
        for sink in self.sinks:
            tk.Radiobutton(self.sinksFrame, text=sink.description, variable='', value=sink.name, command=lambda sink=sink: self.changeSink(sink)).grid(sticky='w')

    def changeSink(self, sink):
        subprocess.check_output(['pacmd', 'set-default-sink', sink.name])
        output = subprocess.check_output(['pacmd', 'list-sink-inputs'])
        inputsIndexes = re.findall(".*index: (.*)", output)
        for index in inputsIndexes:
            subprocess.check_output(['pacmd', 'move-sink-input', index, sink.name])

sinkSwitcher = Application()
sinkSwitcher.master.title('Pulse Sink & Input Switcher')
sinkSwitcher.mainloop()
