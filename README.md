# Python Terminal
This is a project that emulates standard Linux/Unix commands along with associative arguments, without the need for third party libraries, as it is intended to use only the standard default Python3 libraries; as well as the standard default [MicroPython](https://micropython.org/) libraries (for the [MicroPython port](ports/micropython/)), this project is intended for use on any form of device, but is in development for low spec devices, that support the Python language, or sufficient Python like alternatives. This project is still in development, and any contributions would be much appreciated!

This project is aimed to be used in an encapsulated environment (although it is not necessary). And shall mimic basic/key Linux/Unix commands, the project is currently aiming to mimic the following commands (+ implemented / - not implemented yet):
 ```diff
 + alias
 - unalias
 + cat 
 + cd
 + exit
 - ed
 - find
 + head
 + tail
 - kill
 + ls
 + login
 + logout
 + shutdown
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
Certain commands have been omitted from the [MicropPython port](ports/micropython/), for operational purposes!

#### How to run
Simply execute the file named ```terminal.py``` to run the program.

#### How to preconfigure file system
All files within the ```sys/``` directory are as presented in their default layout, and changes made to the layout of any content nested within the directory structure needs to be updates before being run within the Python terminal; this can be done by executing the file ```mkfs.py``` which builds the file structure from ```sys/``` directory and stores the contents into fs.py to be loaded when setting up the emulation.

#### Ports
##### MicroPython
Located in [```ports/mircopython```](ports/micropython). This port is designed and intended for use with the [MicroPython](https://micropython.org/) compiler/interpreter, with this in mind certain attributes of the system had to be removed to allow for the program to work well within the confounds of the [MicroPython language](https://docs.micropython.org/en/latest/reference/index.html), this resulted in threaded commands being ommitted from this build.

#### Future plans
* Add support for the Linux/Unix `chmod` command to be mimicked
