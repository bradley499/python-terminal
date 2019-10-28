# Python 
This is a project that emulates standard Linux/Unix commands along with associative arguments, without the need for third party libraries, as it is intended to user only the standard default Python3 libraries, this project is intended for use on low spec devices, that support the Python language, or sufficent Python like alternatives, such as [MicroPython](https://github.com/micropython/micropython). This project is still in development, and any contributions would be much appreciated!

This project is aimed to be used in an encapsulated environment (although it is not nessecary). And shall mimic basic/key Linux/Unix commands, the project is currently aiming to mimic the following commands (+ implemented / - not implemenetd yet):
 ```diff
 - cat 
 + cd
 - exit
 - find
 - head
 - kill
 + ls
 + mkdir
 + rmdir
 - rm
 - mv
 - ps
 - ping
 + pwd
 - whoami
 - uname
 + hostname
 ```

#### Future plans
* Restrict the terminal to a base directory<sup>[1]</sup> so that it cannot branch out into core system directories
* Add a file registry<sup>[2]</sup> and allocation based on user permissions
* Add support for the Linux/Unix `chmod` command to be mimicked, to hold data in a file registry that will support the entire encapsulated file system from within the base directory[1] folder 
