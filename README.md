# Python Terminal
This is a project that emulates standard Linux/Unix commands along with associative arguments, without the need for third party libraries, as it is intended to user only the standard default Python3 libraries, this project is intended for use on any form of device, but is in development for low spec devices, that support the Python language, or sufficent Python like alternatives. This project is still in development, and any contributions would be much appreciated!

This project is aimed to be used in an encapsulated environment (although it is not nessecary). And shall mimic basic/key Linux/Unix commands, the project is currently aiming to mimic the following commands (+ implemented / - not implemenetd yet):
 ```diff
 + alias
 + cat 
 + cd
 + exit
 - find
 + head
 + tail
 - kill
 + ls
 + login
 + logout
 + mkdir
 + rmdir
 + link
 + unlink
 + rm
 + mv
 + cp
 - ps
 + ping
 + pwd
 + useradd
 + groupadd
 + id
 + whoami
 + uname
 + hostname
 + echo
 + grep
 + uniq
 + wget
 + clear
 + help
 + man
 ```

#### How to run
Simply execute the file named ```terminal.py``` to run the program.

#### Future plans
* Add support for the Linux/Unix `chmod` command to be mimicked