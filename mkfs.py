import os
import time
import os.path
t = [time.time()]
vfs = [ 
	os.path.join(parent, name)[3:]
	for (parent, subdirs, files) in os.walk("sys")
	for name in files + subdirs
]
t.append(time.time())
vfs = sorted(vfs)
t.append(time.time())
fs = []
for file in vfs:
	if os.path.isdir("sys"+file):
		fs.append((file,True))
	else:
		with open("sys"+file,"rb") as file_content:
			fs.append((file,file_content.read()))
t.append(time.time())
with open("fs.py","w") as sfs:
	sfs.write("vfs="+str(repr(fs)))
t.append(time.time())
def to_ms(time):
	return int(time * 1000)
print("Scanned file system in: " + str(to_ms(t[1]-t[0]))+"ms\nStructured file system in: " + str(to_ms(t[2]-t[1]))+"ms\nBuilt file system in: " + str(to_ms(t[3]-t[2]))+"ms\nSaved file system in: " + str(to_ms(t[4]-t[3]))+"ms")