#!/usr/bin/env python3
# terminal.py
import system
import core
import threading
import time
terminal = system.sys

while True:
    response = (core.terminal_parse(input(terminal.get_hostname() + ":" + terminal.get_cwd() + "$ "),True,terminal))
    if not response in ["",None] :
        print(response)