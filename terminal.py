#!/usr/bin/env python3
# terminal.py
import system
import core
import threading
import time
terminal = system.sys

def term_input():
	try:
		return input()
	except KeyboardInterrupt:
		return EOFError

def term_output(output,mode = 0):
	if mode == 0:
		print(output)
	elif mode == 1:
		print(output,end="")
	else:
		term_output(output,0) # rebound output to standard outputting mode

def term_output_non_breaking(output):
	term_output(output,1)

# Set up input/output methods
terminal.set_input_method(term_input,0)
terminal.set_input_method(term_input,1)
terminal.set_output_method(term_output,0)
terminal.set_output_method(term_output_non_breaking,1)
terminal.set_definition(True)


while True:
	try:
		response = (core.terminal_parse(input(terminal.get_hostname() + ":" + terminal.get_cwd() + "$ "),True,terminal))
		if not response in ["",None] :
			print(response)
	except EOFError:
		break
	except SystemExit as e:
		if str(e) == "exit":
			break
		elif str(e) == "clear":
			print("\033c", end="")