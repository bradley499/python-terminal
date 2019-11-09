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

terminal.set_input_method(term_input,0)

while True:
    response = (core.terminal_parse(input(terminal.get_hostname() + ":" + terminal.get_cwd() + "$ "),True,terminal))
    if not response in ["",None] :
        print(response)