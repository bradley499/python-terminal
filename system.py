#!/usr/bin/env python3
# system.py
import core
import proc
from threading import Thread
global proc

base_dir = "root"
if base_dir == False:
	print("STOP!")
	exit()
sys = core.core(base_dir)
proc = proc.proc()