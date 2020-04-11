#!/usr/bin/env python3
# system.py
import core

base_dir = "root"
if base_dir == False:
	print("STOP!")
	exit()
sys = core.core(base_dir)