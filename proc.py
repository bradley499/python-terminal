#!/usr/bin/env python3
# proc.py

import time
from threading import Thread
class proc():
	def __init__(self,pid_max=32768):
		self.processes = {}
		self.pid_max = pid_max
		self.end_processes = []
		self.dying_processes = []
		self.new("_proc",True)
	def run(self):
		while True:
			time.sleep(1)
	def new(self, command = False, foreground = True):
		if command != False:
			new_process_id = self.get_new_process_id()
			if new_process_id >= 0:
				self.processes[new_process_id] = [command,new_process_id,time.time(),foreground,[]]
				return [True,new_process_id]
			else:
				return [False,"Resource temporarily unavailable"]
	def kill(self,pid=0):
		if pid in self.get_all_process_ids():
			self.end_processes.append(pid)
			timeout = time.time() + 2
			while time.time() < timeout:
				if pid in self.get_all_process_ids():
					time.sleep(0.25)
				else:
					break
			if pid in self.get_all_process_ids():
				if pid in self.dying_processes:
					return [False,"Process is still dying..."]
				else:
					return [False,"Unable to kill process"]
			del self.processes[pid]
			return [True,True]
		else:
			return [False,"No process exists"]
	def me(self,pid):
		if pid in self.end_processes:
			return False
		elif pid in self.get_all_process_ids():
			return True
		else:
			return False
	def end(self,pid):
		if pid in self.dying_processes:
			self.dying_processes.remove(pid)
		del self.processes[pid]
	def ending(self,pid):
		if not pid in self.dying_processes:
			self.dying_processes.append(pid)
			return True
		else:
			return False
	def pid_output(self,pid=0, output=None):
		if output != None:
			if pid in self.get_all_process_ids():
				self.processes[pid][4].append([output,time.time(),False])
	def fg_output(self,pid=0):
		if pid in self.get_all_process_ids():
			outputs = self.processes[pid][4]
			for output in outputs:
				if not output[2]:
					print(output[0])
				del outputs[0]
			self.processes[pid][4] = outputs
	def get_all_process_ids(self):
		process_ids = []
		for process_id in self.processes.keys():
			process_ids.append(process_id)
		return process_ids
	def get_new_process_id(self):
		process_ids = self.get_all_process_ids()
		for pid in range(self.pid_max):
			if not pid in process_ids:
				return pid
		return -1