#!/usr/bin/env python3
# terminal.py
import system
import core
import threading
import time
import getpass
terminal = system.sys

def term_input():
	try:
		return input()
	except KeyboardInterrupt:
		return EOFError

def term_pass_input():
	try:
		return getpass.getpass("")
	except KeyboardInterrupt:
		return EOFError

def term_output(output,mode = 0):
	if mode == 0:
		print(output, flush=True)
	elif mode == 1:
		print(output,end="",flush=True)
	else:
		term_output(output,0) # rebound output to standard outputting mode

def term_output_non_breaking(output):
	term_output(output,1)

# Set up input/output methods
terminal.set_input_method(term_input,0)
terminal.set_input_method(term_input,1)
terminal.set_input_method(term_pass_input,2)
terminal.set_output_method(term_output,0)
terminal.set_output_method(term_output_non_breaking,1)
terminal.set_definition(True)


while True:
	if terminal.user == None or terminal.group == None:
		terminal.login([])
	try:
		response = (core.terminal_parse(input("\033[92m"+terminal.who_am_i()+"@"+terminal.get_hostname()+"\033[0m:\033[;34m"+terminal.get_display_cwd()+"\033[0m$ "),True,terminal))
		if not response in ["",None] :
			print(response)
	except EOFError:
		break
	except SystemExit as e:
		if str(e) == "exit":
			break
		elif str(e) == "clear":
			print("\033c", end="")