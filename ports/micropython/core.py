#!/usr/bin/env python3
# core.py

import os
import os.path
import json
import system
import version
import utime as time
import math
import usocket as socket
import ussl
import ustruct as struct
import uselect as select
import uhashlib
import ubinascii
import uhashlib
import urandom as random
import ure as re

class core():
	def __init__(self,base_dir="root/"):
		self.set_all_command_bases()
		self.dir = False
		self.pipe_in = None
		self.process_id = None
		self.input_method_reference = [[None,False],[None,False],[None,False]]
		self.output_method_reference = [[None,False],[None,False]]
		self.definition_complete = False
		self.base_directory = base_dir
		self.rel_base_directory = os.getcwd()
		self.env_vars = {}
		self.alias_vars = {}
		self.stable = False
		self.user = None
		self.group = None
		self.sys_groups = {}
		self.buffer = 512
		self.set_cwd(self.rel_base_directory)

	def set_all_command_bases(self, args=[]):
		self.command_bases = {"pwd":[self.get_display_cwd,["string"],False,False],"ls":[self.ls,["join"," "],False,False],"uname":[self.uname,["join"," "],False,False],"hostname":[self.get_hostname,["string"],False,False],"whoami":[self.who_am_i,["string"],False,False],"cd":[self.change_directory,["string/void"],False,True],"mkdir":[self.create_directory,["join/void","\n"],False,True],"rmdir":[self.remove_directory,["join/void","\n"],False,True],"cat":[self.concatenate,["join","\n"],False,True],"head":[self.head,["join","\n"],False,True],"tail":[self.tail,["join","\n"],False,True],"cp":[self.copy,["join/void","\n"],False,True],"mv":[self.move,["join/void","\n"],False,True],"link":[self.link,["string"],False,True],"unlink":[self.unlink,["string"],False,True],"rm":[self.remove,["join/void","\n"],False,True],"clear":[self.clear,["null"],False,False],"echo":[self.echo,["join/void"," "],False,False],"touch":[self.touch,["join/void"," "],False,True],"alias":[self.alias,["join/void","\n"],False,True],"unalias":[self.unalias,["join/void","\n"],False,True],"login":[self.login,["join/void","\n"],False,False],"logout":[self.logout,["join/void","\n"],False,False],"shutdown":[self.shutdown,["join/void","\n"],False,False],"passwd":[self.passwd,["join/void","\n"],False,True],"useradd":[self.useradd,["join/void","\n"],False,False],"groupadd":[self.groupadd,["join/void","\n"],False,False],"id":[self.id,["join/void"," "],False,False],"grep":[self.grep,["join/void","\n"],True,True],"uniq":[self.uniq,["join/void","\n"],True,True],"sort":[self.sort,["join/void","\n"],True,True],"wget":[self.wget,["join/void","\n"],True,True],"help":[self.help,["join","\n"],False,False],"man":[self.man,["join","\n"],False,False]}
		return True

	def get_all_command_bases(self, args=[]):
		self.set_all_command_bases()
		return self.command_bases

	def set_definition(self,complete = False):
		self.definition_complete = complete == True
		unpack = False
		if self.definition_complete:
			self.output_method(1,"Scanning for file system...  ")
			base_dir_exists = self.change_directory([self.base_directory]) == None
			self.output_method(0,"[" + {True:"Success",False:"Failed"}[base_dir_exists] + "]")
			if not base_dir_exists:
				self.output_method(1,"Creating host file system... ")
				os.mkdir(self.base_directory)
				if self.change_directory([self.base_directory]) != None:
					self.output_method(0,"[Failed]")
					for x in range(0,3):
						self.output_method(0,"")
					self.output_method(0,"Failed to boot!")
					self.output_method(0,"Unable to securely created restricted filesystem,")
					self.output_method(0,"which resulted in the system exitting the boot")
					self.output_method(0,"sequence; system will not boot further. Error in:")
					self.output_method(0,self.base_directory)
					self.base_directory = False
					raise SystemExit()
				else:
					self.output_method(0,"[Success]")
					unpack = True
			else:
				self.base_directory = os.getcwd()
			self.change_directory(self.rel_base_directory)
			self.change_directory(["/"])
			self.base_directory = self.dir_abspath(self.base_directory)
		self.stable = True
		self.change_directory(["/"])
		if unpack:
			self.output_method(1,"Unpacking file system...     ")
			if True:
				import fs
				for file in fs.vfs:
					if file[1] == True:
						self.create_directory([file[0]])
					else:
						with open(self.base_directory+file[0],"wb") as vfs:
							vfs.write(file[1])
				self.output_method(0,"[Success]")
			else:
				self.output_method(0,"[Failed]")
				raise SystemExit("exit")
		self.output_method(1,"Discovering environments...  ")
		invalid_conf_files = []
		if self.change_directory(["/etc"]) != None:
			if self.change_directory(["etc"]) != None:
				self.output_method(0,"[Failed]")
		self.change_directory(["/"])
		if self.change_directory(["etc"]) == None:
			directory_contents = self.ls(["-A","-p","--color","never"])
			for file in directory_contents:
				if file.endswith("/"):
					continue
				elif file.endswith(".defs"):
					env_conf = file[0:-5]
					self.env_vars[env_conf] = []
					with open(file,"r") as file_contents:
						file_contents = file_contents.readlines()
						if len(file_contents) == 0:
							invalid_conf_files.append(env_conf)
							continue
						for variable in file_contents:
							if "=" in variable:
								variable = variable.split("=")
								if len(variable) > 2:
									variable[1] = variable[1:].join("=")
								elif len(variable) == 1:
									variable[1] = ""
								variable[1] = variable[1].rstrip()
								iteration_position = 0
								for variable_data in self.env_vars[env_conf]:
									if variable_data[0] != variable[0]:
										iteration_position += 1
										continue
									else:
										del self.env_vars[env_conf][iteration_position]
										break
								del iteration_position
								self.env_vars[env_conf].append(variable)
								del variable
							else:
								del self.env_vars[env_conf]
								invalid_conf_files.append(env_conf)
								break
		self.change_directory(["/"])
		if self.change_directory(["etc"]) == None:
			if self.env_vars == []:
				self.output_method(0,"[Failed]")
			else:
				self.output_method(0,"[" + {True:"Success",False:"Partial"}[len(invalid_conf_files) == 0] + "]")
				if len(invalid_conf_files) > 0:
					for failed_env_var_host in invalid_conf_files:
						self.output_method(0,"Invalid environment host: " + failed_env_var_host)
		self.change_directory(["/"])
		self.output_method(1,"Generating relations...      ")
		self.alias(["exit","'logout'"])
		self.alias(["la","'ls -A'"])
		self.alias(["ls","'ls --color=auto'"])
		self.output_method(0,"[Success]")
		self.output_method(1,"Gathering user groups...     ")
		system_usergroup_ids = self.id([])
		system_usergroup_id = {"system":False,"root":False}
		for base_group in system_usergroup_id.keys():
			base_group = base_group
			for gid in system_usergroup_ids:
				gid = gid.split("(")
				if len(gid) > 2:
					gid[1] = "(".join(gid[1:])
				gid[1] = gid[1].split(")")
				if len(gid[1]) > 2 and type(gid[1]) == list:
					gid[1] = gid[1][:-1]
				if len(gid[1]) > 1 and type(gid[1]) == list:
					gid[1] = gid[1][0]
				if base_group == gid[1]:
					gid[0] = gid[0].split("gid=")
					if len(gid[0]) > 1 and type(gid[0]) == list:
						gid[0] = gid[0][1:]
						gid[0] = gid[0][0]
						if gid[0].isdigit():
							system_usergroup_id[base_group] = int(gid[0])
		if False in [system_group_id != False for system_group_id in system_usergroup_id.values()]:
			self.output_method(0,"[Missing]")
			self.output_method(1,"Creating user groups...      ")
			for base_group in system_usergroup_id.keys():
				if system_usergroup_id[base_group] == False:
					system_usergroup_id[base_group] = self.groupadd([base_group])
		self.sys_groups = system_usergroup_id
		self.output_method(0,"[Success]")
		self.output_method(1,"Searching for users...       ")
		valid_uids = []
		if os.path.exists(self.base_directory + "/etc/passwd"):
			uids = self.concatenate(["/etc/passwd"])
			for uid in uids:
				uid = uid.split(":")
				if len(uid) == 5:
					uid.pop()
					if uid[3].isdigit():
						if uid[2].isdigit():
							uid[2] = int(uid[2])
							uid = [int(uid.pop(3)),str(uid.pop(0)),uid]
							uid.append(uid[2].pop(0))
							uid[2] = uid[2][0]
							uid = tuple(uid)
							valid_uids.append(uid)
		self.output_method(0,"[" + {True:"Success",False:"Missing"}[len(valid_uids) > 0] + "]")
		if len(valid_uids) == 0:
			self.output_method(0,"")
			self.output_method(0,"Please create a default user account.")
			password = (3,)
			password_hide = (3,4)
			user_requirements_display = {"comment":"Enter your name","hostname":"Name your computer","LOGIN":"Enter new username","password":"Enter password","password2":"Retype your password"}
			user_requirements = {"comment":False,"hostname":False,"LOGIN":False,"password":False,"password2":False}
			user_requirement_layout = ["comment","hostname","LOGIN","password","password2"]
			valid = False
			while not valid:
				requirement_iteration = 0
				for user_requirement in user_requirement_layout:
					user_requirement_input = user_requirements[user_requirement]
					while user_requirement_input == False:
						self.output_method(1,user_requirements_display[user_requirement]+": ")
						user_requirement_input = self.input_method({True:2,False:0}[requirement_iteration in password_hide])
						if len(user_requirement_input.strip()) == 0:
							user_requirement_input = False
						else:
							if requirement_iteration not in password:
								user_requirement_input = user_requirement_input.lstrip().rstrip()
								user_requirement_input = user_requirement_input.strip()
								user_requirement_input_build = []
								allow_single_space = requirement_iteration != 2
								for user_requirement_input_sub in user_requirement_input:
									if user_requirement_input_sub.strip() == user_requirement_input_sub:
										user_requirement_input_build.append(user_requirement_input_sub)
									elif allow_single_space:
										if len(user_requirement_input_build) > 0:
											if user_requirement_input_build[-1] != " ":
												user_requirement_input_build.append(user_requirement_input_sub)
								user_requirement_input = "".join(user_requirement_input_build)
								user_requirement_input = user_requirement_input.lstrip().rstrip()
							user_requirements[user_requirement] = user_requirement_input
					if requirement_iteration in password:
						user_requirements[user_requirement] = self.passwd([],user_requirements[user_requirement],False)
					requirement_iteration += 1
				valid = self.passwd([],user_requirements["password2"],user_requirements["password"])
				if not valid:
					self.output_method(0,"Sorry, passwords do not match.")
					user_requirements[list(user_requirements.keys())[password_hide[0]]] = False
					user_requirements[list(user_requirements.keys())[password_hide[1]]] = False
			del user_requirements[list(user_requirements.keys())[-1]]
			self.output_method(0,"")
			self.output_method(1,"Creating user account...     ")
			try:
				if self.useradd([user_requirements["LOGIN"],"-c",user_requirements["comment"],"-g",str(system_usergroup_id["root"])]) == None:
					with open(self.base_directory + "/etc/shadow","a+") as shadow_file:
						shadow_file.write(user_requirements["LOGIN"] + ":" + user_requirements["password"] + "\n")
					with open(self.base_directory + "/etc/hostname","w") as shadow_file:
						shadow_file.write(user_requirements["hostname"])
					self.output_method(0,"[Success]")
					self.user = user_requirements["LOGIN"]
					if os.path.exists(self.base_directory + "/etc/passwd"):
						uids = self.concatenate(["/etc/passwd"])
						for uid in uids:
							uid = uid.split(":")
							if len(uid) == 5:
								uid.pop()
								if uid[3].isdigit():
									if uid[2].isdigit():
										uid[2] = int(uid[2])
										uid = [int(uid.pop(3)),str(uid.pop(0)),uid]
										uid.append(uid[2].pop(0))
										uid[2] = uid[2][0]
										uid = tuple(uid)
										valid_uids.append(uid)
					uid_exists = -1
					while uid_exists < 0:
						for uid in valid_uids:
							if uid[1] == self.user:
								uid_exists = uid
								break
						if uid_exists == -1:
							uid_exists = 0
						elif type(uid_exists) == tuple:
							break
					self.group = [int(system_usergroup_id["root"]),(uid_exists[0],uid_exists[2],uid_exists[3])]
					self.alias(["$USER","'" + user_requirements["LOGIN"] + "'","$LOGNAME","'" + user_requirements["LOGIN"] + "'"])
				else:
					self.output_method(0,"[Failed]")
			except ProcessLookupError:
				self.output_method(0,"[Failed]")
			self.output_method(0,"")
			self.welcome()
		if self.user == None:
			self.output_method(0,"")
			self.login([])

	def get_definition(self):
		return self.definition_complete

	def directory_restrict(self,to_dir=False):
		if self.base_directory == False or self.stable == False:
			return (to_dir,to_dir)
		else:
			path = to_dir.split(self.base_directory)
			if len(path) > 1:
				path = self.base_directory.join(path[1:])
			else:
				path = path[0]
			path_valid = path != to_dir
			if path_valid:
				return (to_dir,path)
			else:
				return (self.base_directory,"/")

	def dir_normpath(self,path):
		path = self.directory_restrict(path)[0]
		path = path.split("/")
		structured_path = []
		for directory in path:
			if directory == "..":
				if len(structured_path) > 0:
					structured_path.pop()
			elif directory != ".":
				structured_path.append(directory)
		if len(structured_path) == 0:
			return "/"
		if structured_path[0] == "":
			if len(structured_path) == 1:
				structured_path[0] = "."
		return "/".join(structured_path)

	def dir_abspath(self,path):
		if len(path) > 0:
			if path[0] != "/":
				return os.getcwd() + "/" + path
			else:
				path = self.dir_normpath(path)
		path = self.directory_restrict(path)
		path = path[0]
		return path

	def set_input_method(self,inputting_method = False, mode = -1):
		if inputting_method != False and mode in range(len(self.input_method_reference)):
			if callable(inputting_method):
				self.input_method_reference[mode] = [inputting_method, True]
				return self.input_method_reference[mode];
			else:
				return [ImportWarning("failed attempt to implement a non callable inputting method"),False]
		else:
			return [ImportWarning("failed to implement an input method from no prescribed source"),False]

	def input_method(self,mode,additions=False):
		if self.input_method_reference == [[None,False],[None,False]]:
			raise NotImplementedError("no input method defined")
		else:
			if mode == 0: # single line
				if self.input_method_reference[0][1]:
					try:
						return self.input_method_reference[0][0]() or " "
					except:
						raise EOFError()
				else:
					raise NotImplementedError("no input mehod defined")
			elif mode == 1: # response value input
				if self.input_method_reference[1][1]:
					if not additions == False:
						self.output_method(1,additions)
					return self.input_method_reference[1][0]() or " "
				else:
					raise NotImplementedError("no input method defined")
			elif mode == 2:
				if self.input_method_reference[2][1]:
					return self.input_method_reference[2][0]() or ""
				else:
					raise NotImplementedError("no input method defined")
			else:
				raise NotImplementedError("no input method defined")

	def set_output_method(self,outputting_method = False, mode = -1):
		if outputting_method != False and mode != -1:
			if mode == 0:
				if callable(outputting_method):
					self.output_method_reference[0] = [outputting_method, True]
					return self.output_method_reference[0];
				else:
					return [ImportWarning("failed attempt to implement a non callable outputting method"),False]
			elif mode == 1:
				if callable(outputting_method):
					self.output_method_reference[1] = [outputting_method, True]
					return self.output_method_reference[1];
				else:
					return [ImportWarning("failed attempt to implement a non callable outputting method"),False]
		else:
			return [ImportWarning("failed to implement an output method from no prescribed source"),False]

	def output_method(self,mode=0,output=""):
		if not self.output_method_reference[1]:
			raise NotImplementedError("no output method defined")
		else:
			if mode == 0: # continuous
				self.output_method_reference[0][0](output)
			elif mode == 1: # non breaking output (typical input method is followed)
				self.output_method_reference[1][0](output)
			else:
				raise NotImplementedError("no output method defined")
		return output

	def pretty_time(self,time_display=False,show_day_of_week=False,format_string=False):
		if time_display == False:
			time_display = time.time()
		time_display = time.localtime(time_display)
		if format_string != False:
			return format_string.replace("%Y",str(time_display[0])).replace("%m",{True:"0",False:""}[len(str(time_display[1])) == 1] + str(time_display[1])).replace("%m",{True:"0",False:""}[len(str(time_display[1])) == 1] + str(time_display[1])).replace("%d",{True:"0",False:""}[len(str(time_display[2])) == 1] + str(time_display[2])).replace("%H",{True:"0",False:""}[len(str(time_display[3])) == 1] + str(time_display[3])).replace("%M",{True:"0",False:""}[len(str(time_display[4])) == 1] + str(time_display[4])).replace("%S",{True:"0",False:""}[len(str(time_display[5])) == 1] + str(time_display[5]))
		else:
			time_display = {True:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][time_display[6]] + " ",False:""}[show_day_of_week == True] + ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][time_display[1]-1] + " " + {True:"0",False:""}[len(str(time_display[2])) == 1] + str(time_display[2]) + " " + {True:"0",False:""}[len(str(time_display[3])) == 1] + str(time_display[3]) + ":" + {True:"0",False:""}[len(str(time_display[4])) == 1] + str(time_display[4]) + ":" + {True:"0",False:""}[len(str(time_display[5])) == 1] + str(time_display[5]) + " " + str(time_display[0])
		return time_display

	def login(self,args=[]):
		response = []
		preserve_environment = False
		pre_authed = False
		username = False
		for arg in args:
			if arg.startswith("-"):
				if arg == "-p":
					preserve_environment = True
				elif arg == "-f":
					pre_authed = True
				else:
					raise ValueError(arg)
			elif username == False:
				username = arg
			else:
				raise ValueError(arg)
		if pre_authed and username == False:
			return ["login: no LOGIN was preauthenticated"]
		while True:
			user_login_values = {"username":False,"password":False}
			user_login_display = {"username":self.get_hostname([]) + " login","password":"Password"}
			ordered_user_login_display = ["username","password"]
			for user_login_display_reference in ordered_user_login_display:
				user_login_breif = user_login_display_reference
				user_login_value = user_login_values[user_login_display_reference]
				while user_login_value == False:
					if username == False:
						self.output_method(1,user_login_display[user_login_breif] + ": ")
						user_login_value = self.input_method({True:2,False:0}[user_login_breif == "password"])
					else:
						user_login_value = username
						username = False
					user_login_value = user_login_value.lstrip().rstrip()
					user_login_value = user_login_value.strip()
					user_login_build = []
					for user_login_sub in user_login_value:
						if user_login_sub.strip() == user_login_sub:
							user_login_build.append(user_login_sub)
					user_login_value = "".join(user_login_build)
					user_login_value = user_login_value.lstrip().rstrip()
					if len(user_login_value) == 0 and user_login_breif != "password":
						user_login_value = False
					else:
						user_login_values[user_login_breif] = user_login_value
			valid_uids = []
			if os.path.exists(self.base_directory + "/etc/passwd"):
				uids = self.concatenate(["/etc/passwd"])
				for uid in uids:
					uid = uid.split(":")
					if len(uid) == 5:
						uid.pop()
						if uid[3].isdigit():
							if uid[2].isdigit():
								uid[2] = int(uid[2])
								uid = [int(uid.pop(3)),str(uid.pop(0)),uid]
								uid.append(uid[2].pop(0))
								uid[2] = uid[2][0]
								uid = tuple(uid)
								valid_uids.append(uid)
			uid_exists = -1
			uid_generations = 0
			while uid_exists < 0:
				for uid in valid_uids:
					if uid[1] == user_login_values["username"]:
						uid_exists = uid
						break
				if uid_exists == -1:
					uid_exists = 0
				elif type(uid_exists) == tuple:
					break
			if uid_exists == 0:
				user_login_values = {"username":False,"password":False}
			else:
				password_hash = False
				if uid_exists[3] != "x":
					password_hash = uid_exists[3]
				else:
					if os.path.exists(self.base_directory + "/etc/shadow"):
						password_hash = self.concatenate(["/etc/shadow"])
						for password in password_hash:
							password = password.split(":")
							if len(password) >= 2:
								password_hash_temp = password.pop(-1)
								password = ":".join(password)
								if password == uid_exists[1]:
									password_hash = password_hash_temp
									break
				if password_hash == False or type(password_hash) == list:
					self.output_method(0,"Unable to locate password for '" + user_login_values["username"] + "'")
				else:
					if self.passwd([],user_login_values["password"],password_hash):
						self.alias(["$USER","'" + user_login_values["username"] + "'","$LOGNAME","'" + user_login_values["username"] + "'"])
						self.user = user_login_values["username"]
						self.group = [uid_exists[0],uid_exists[1:]]
						if not preserve_environment:
							current_directory = self.get_display_cwd()
							self.change_directory(["/"])
							if self.change_directory(["etc"]) == None:
								directory_contents = self.ls(["-A","-p","--color","never"])
								for file in directory_contents:
									if file.endswith("/"):
										continue
									elif file.endswith(".defs"):
										env_conf = file[0:-5]
										self.env_vars[env_conf] = []
										with open(file,"r") as file_contents:
											file_contents = file_contents.readlines()
											if len(file_contents) == 0:
												invalid_conf_files.append(env_conf)
												continue
											for variable in file_contents:
												if "=" in variable:
													variable = variable.split("=")
													if len(variable) > 2:
														variable[1] = variable[1:].join("=")
													elif len(variable) == 1:
														variable[1] = ""
													variable[1] = variable[1].rstrip()
													iteration_position = 0
													for variable_data in self.env_vars[env_conf]:
														if variable_data[0] != variable[0]:
															iteration_position += 1
															continue
														else:
															del self.env_vars[env_conf][iteration_position]
															break
													del iteration_position
													self.env_vars[env_conf].append(variable)
													del variable
												else:
													del self.env_vars[env_conf]
													invalid_conf_files.append(env_conf)
													break
							self.change_directory([current_directory])
							self.change_directory(["/"])
							self.get_env_vars()
						self.output_method(0,"")
						self.welcome()
						return None
			uid_exists = -1
		return

	def welcome(self,prepend=None):
		if prepend != None:
			if type(prepend) != list:
				prepend = list(prepend)
			for prepend_out in prepend:
				if type(prepend_out) in [str,int]:
					prepend_out = str(prepend_out)
					self.output_method(0,str(prepend_out))
		self.output_method(0,"Welcome to μOS " + str(version.__version__))
		self.output_method(0,"")

	def logout(self,args=[]):
		self.user = None
		self.group = None
		self.output_method(0,"")
		raise SystemExit("logout")
		return None

	def shutdown(self,args=[]):
		reset = False
		confirmed = False
		for arg in args:
			if arg in ["--reset"]:
				reset = True
			elif arg in ["--confirm"]:
				confirmed = True
			else:
				raise ValueError(arg)
		if reset:
			valid = False
			for group in self.sys_groups.values():
				if group == self.group[1][1]:
					valid = True
					break
			if not valid:
				return ["A privileged account is required to complete this action!"]
			if confirmed:
				self.output_method(1,"Resetting system... ")
				self.change_directory(["/"])
				self.remove(["*","-r","-v"])
				try:
					os.rmdir(self.base_directory)
					self.output_method(0,"[Done]")
				except:
					self.output_method(0,"[Failed]")
			else:
				return ["To reset your system you must also include --confirm"]
		self.output_method(0,"Shutting down...")
		try:
			self.logout()
		except:
			pass
		raise SystemExit("exit")

	def set_cwd(self,directory=False):
		if directory == False:
			return False
		else:
			if self.stable:
				if directory.startswith("/"):
					directory = self.base_directory + directory
				else:
					directory = self.get_cwd() + "/" + directory
			else:
				if directory == "/":
					directory = self.rel_base_directory + "/"
			directory = self.dir_abspath(directory)
			if self.stable:
				directory = self.directory_restrict(directory)[0]
			if len(directory) > 1:
				while directory[-1] == "/" and len(directory) > 1:
					directory = directory[:-1]
			self.dir = directory
			if self.base_directory != False and self.stable:
				os.chdir(directory)
			else:
				os.chdir(self.dir)
			return self.dir

	def get_env_vars(self,host=False,keyed=False):
		if host == False:
			return {True:{},False:[]}[keyed]
		else:
			if host in self.env_vars:
				environments = self.env_vars[host]
				environment_keyed = {}
				if keyed:
					for variable in environments:
						environment_keyed[variable[0]]=variable[1]
					environments = environment_keyed
				return environments
			else:
				return {True:{},False:[]}[keyed]

	def passwd(self,args=[],password=False,hashed_password=False):
		user_login = False
		for arg in args:
			if user_login != False:
				return ["passwd: user LOGIN is already provided"]
				break
			user_login = arg

		if password != False or hashed_password != False:
			try:
				password = ubinascii.hexlify(uhashlib.md5(password).digest()).decode("utf-8")
			except:
				return False
			if hashed_password == False:
				return password
			else:
				return password == hashed_password
		else:
			password_hash = False
			user_defined_login = True
			if user_login == False:
				user_defined_login = False
				user_login = self.user
			if os.path.exists(self.base_directory + "/etc/shadow"):
				password_hash = self.concatenate(["/etc/shadow"])
				for password in password_hash:
					password = password.split(":")
					if len(password) >= 2:
						password_hash_temp = password.pop(-1)
						password = ":".join(password)
						if password == user_login:
							password_hash = password_hash_temp
							break
			if password_hash == False:
				if not user_defined_login:
					return ["passwd: Unable to locate passwords for current user","passwd: password unchanged"]
			cpwd = True
			if password_hash != False and not user_defined_login:
				self.output_method(1,"Current password: ")
				cpwd = self.input_method(2)
				cpwd = self.passwd([],cpwd,password_hash)
			if cpwd:
				del cpwd
				while True:
					self.output_method(1,"New password: ")
					npwd = [self.input_method(2),False]
					self.output_method(1,"Retype new password: ")
					npwd[1] = self.input_method(2)
					if len(npwd[0].strip()) == 0:
						self.output_method(0,"No password supplied")
					else:
						break
				if npwd[0] != npwd[1]:
					return ["Sorry, passwords do not match.","passwd: Authentication token manipulation error","passwd: password unchanged"]
				else:
					npwd = self.passwd([],npwd[0],False)
					passwords = []
					password_hash = self.concatenate(["/etc/shadow"])
					user_match = False
					for password in password_hash:
						password = password.split(":")
						if len(password) >= 2:
							password_user = ":".join(password)
							if password_user == user_login:
								user_match = True
								password = [password_user,npwd]
						passwords.append(":".join(password))
					if not user_match:
						passwords.append(user_login + ":" + npwd)
					with open(self.base_directory + "/etc/shadow","w") as shadow_file:
						shadow_file.write("\n".join(passwords)+"\n")
					return ["passwd: password updated successfully"]
			else:
				return ["passwd: Authentication token manipulation error","passwd: password unchanged"]
			return False

	def useradd(self,args=[]):
		response = []
		unique_id = True
		non_unique = False
		key = self.get_env_vars("login",True)
		system = False
		gid = False
		groups = []
		comment = False
		user_name = False
		password = False
		home_dir = False
		if len(args) > 0:
			get_next_parameter = [False,False]
			possible_more = False
			for arg in args:
				if get_next_parameter[0] or possible_more != False:
					get_next_parameter[0] = False
					if possible_more != False:
						get_next_parameter[1] = possible_more
					if get_next_parameter[1] in ["-u","--uid"]:
						if arg.isdigit():
							arg = int(arg)
							if arg > 0:
								unique_id = arg
						return ["useradd: invalid value of '" + arg + "' for " + get_next_parameter[1] + " parameter"] 
					elif get_next_parameter[1] == "-c":
						comment = arg
						continue
					elif get_next_parameter[1] == "-K":
						if type(key) != dict:
							key = {}
						if len(get_next_parameter) != 3:
							if not arg.startswith("-"):
								get_next_parameter[0] = True
								get_next_parameter.append(arg)
								continue
						else:
							key[get_next_parameter[2]] = arg
							del get_next_parameter[2]
							continue
					elif get_next_parameter[1] == "-g":
						groups.insert(0,arg)
						continue
					elif get_next_parameter[1] == "-G":
						if arg != ",":
							continue
						groups.extend(arg.split(","))
						possible_more = {True:"-G",False:False}[len(arg.split(",")[-1]) == 0]
						continue
					elif get_next_parameter[1] == "-p":
						if password != True:
							return ["useradd: password has already been provided"]
						password = arg
					possible_more = False
				if arg.startswith("-"):
					if arg in ["-u","--uid"]:
						unique_id = True
						get_next_parameter = [True,arg]
					elif arg in ["-o","--non-unique"]:
						non_unique = False
					elif arg in ["-K","--key"]:
						key = True
						get_next_parameter = [True,"-K"]
					elif arg in ["-g","-G","--groups","--gid"]:
						get_next_parameter = [True,"-"+{True:"g",False:"G"}[arg in ["-g","--gid"]]]
					elif arg in ["-c","--comment"]:
						comment = True
						get_next_parameter = [True,"-c"]
					elif arg in ["-m","--create-home"]:
						key["CREATE_HOME"] = True
						home_dir = True
					elif arg in ["-p","--password"]:
						password = True
						get_next_parameter = [True,"-p"]
					elif arg in ["-r","--system"]:
						key = self.get_env_vars("login",True)
						try:
							key["UID_MIN"] = key["SYS_UID_MIN"]
							key["UID_MAX"] = key["SYS_UID_MAX"]
						except:
							pass
						system = True
					else:
						raise ValueError(arg)
				elif user_name == False:
					user_name = arg
				else:
					raise ValueError(arg)
			if len(groups) == 0:
				return ["useradd: incomplete argument reference for -" + {True:"g",False:"-gid"}["-g" in args]]
			elif unique_id != True and non_unique:
				return ["useradd: incomplete argument reference for -" + {True:"u",False:"-uid"}["-u" in args]]
			elif comment == True:
				return ["useradd: incomplete argument reference for -" + {True:"c",False:"-comment"}["-c" in args]]
			elif password == True:
				return ["useradd: incomplete argument reference for -" + {True:"p",False:"-password"}["-p" in args]]
			elif user_name == False:
				return ["useradd: expected a LOGIN to be provided"]
			for required in ["UID_MIN","UID_MAX","CREATE_HOME"]:
				if required not in key.keys():
					raise ReferenceError(required)
				else:
					if key[required].isdigit():
						key[required] = int(key[required])
						if key[required] < 0:
							raise ReferenceError(required)
					elif key[required].upper() in ["TRUE","FALSE"]:
						if key[required].upper() == "TRUE":
							key[required] = True
						else:
							key[required] = False

			if unique_id not in [True,False]:
				if non_unique:
					if unique_id > key["UID_MAX"] or unique_id < key["UID_MIN"]:
						return ["useradd: '" + unique_id + "' is out of the bounds of " + str(key["UID_MIN"]) + " and " + str(key["UID_MAX"])]
				else:
					return ["useradd: required permission to add a group with a non-unique UID, try '-o'"]
			if not non_unique:
				try:
					unique_id = randint(key["UID_MIN"],key["UID_MAX"]+1)
				except:
					unique_id = key["UID_MIN"]
			if not os.path.exists(self.base_directory + "/etc/group"):
				raise ProcessLookupError("/etc/group")
			else:
				group_data = self.concatenate(["/etc/group"])
			groups_id_data = {}
			for group_data_ids in group_data:
				group_data_ids = group_data_ids.split(":")
				group_data_ids.pop()
				if len(group_data_ids) >= 3:
					group_relative_data = [":".join(group_data_ids[0:-2]),group_data_ids[-2],group_data_ids[-1]]
					if group_relative_data[2].isdigit():
						group_relative_data[2] = int(group_relative_data[2])
						if not group_relative_data[2] in groups_id_data.keys():
							groups_id_data[group_relative_data[2]] = [group_relative_data[0],group_relative_data[1]]
			group_limit = []
			for group in groups:
				match = False
				for group_id, group_data in groups_id_data.items():
					group = str(group)
					if group.isdigit():
						group = int(group)
						if group == group_id:
							match = True
					elif group_data[0] == group_name:
						match = True
					if not match:
						group_limit.append([group_id,group_data[1],group_data[0]])
				if not match:
					return ["useradd: the provided GID '" + str(group) + "' does not exist"]
			valid_uids = []
			if os.path.exists(self.base_directory + "/etc/passwd"):
				uids = self.concatenate(["/etc/passwd"])
				for uid in uids:
					uid = uid.split(":")
					if len(uid) == 5:
						uid.pop()
						if uid[3].isdigit():
							if uid[2].isdigit():
								uid[2] = int(uid[2])
								uid = [int(uid.pop(3)),str(uid.pop(0)),uid]
								uid.append(uid[2].pop(0))
								uid[2] = uid[2][0]
								uid = tuple(uid)
								valid_uids.append(uid)
			uid_exists = -1
			uid_generations = 0
			while uid_exists != 0:
				for uid in valid_uids:
					if uid[0] == unique_id or uid[1] == user_name:
						uid_exists = 1
						if uid[1] == user_name:
							return ["useradd: the provided LOGIN is already associated to another user"]
					for x in range(len(group_limit)):
						if group_limit[x][1] == "x":
							continue
						if uid[2] == group_limit[x][0]:
							group_limit[x][1] -= 1
				if uid_exists < 0:
					uid_exists = 0
				else:
					if non_unique:
						return ["useradd: the provided UID is already associated to another user"]
					else:
						try:
							unique_id = randint(key["UID_MIN"],key["UID_MAX"]+1)
						except:
							unique_id = key["UID_MIN"]
						uid_generations += 1
						if uid_generations >= 20:
							return ["useradd: the only possible UID from provided boundaries already exists - " + str(key["UID_MIN"])]
			for group_restrict in group_limit:
				if group_restrict[1] == "x":
					pass
				elif group_restrict[1] <= 0:
					return ["useradd: the user group '" + str(group_restrict) + "' cannot accommodate no more users"]
			uid_build = [user_name,{True:password,False:"x"}[password != False],",".join(groups),str(unique_id),{True:"",False:comment}[comment == False]]
			with open(self.base_directory + "/etc/passwd","a+") as passwd_file:
				passwd_file.write(":".join(uid_build)+"\n")
			if key["CREATE_HOME"] == True:
				if not home_dir and system:
					return None
				self.copy(["/etc/skel","/home/" + user_name + "/","-r"],False)
			return None
		return ["useradd: expected a LOGIN to be provided"]

	def id(self,args=[]):
		response = []
		active_group_id = False
		all_group_ids = False
		user = False
		for arg in args:
			if arg.startswith("-"):
				if arg in ["-g","--group"]:
					active_group_id = True
					all_group_ids = False
				elif arg in ["-G","--groups"]:
					all_group_ids = True
					active_group_id = False
				elif arg in ["-u","--user"]:
					user = True
		if user and (active_group_id or all_group_ids):
			return ["id: cannot print 'only' of more than one choice"]
		ids = {}
		if not all_group_ids:
			if os.path.exists(self.base_directory + "/etc/passwd"):
				uids = self.concatenate(["/etc/passwd"])
				for uid in uids:
					uid = uid.split(":")
					if len(uid) == 5:
						uid.pop()
						if uid[3].isdigit():
							if uid[2].isdigit():
								uid[2] = int(uid[2])
								ids[uid[0]] = [str(uid.pop(3)),False]
				del uids
			if user:
				for user_login, user_id in ids.items():
					if user_login == self.user:
						return [user_id[0]]
				return []
		if os.path.exists(self.base_directory + "/etc/group"):
			gids = self.concatenate(["/etc/group"])
			for gid in gids:
				gid = gid.split(":")
				gid.pop()
				if len(gid) == 3:
					gid = [":".join(gid[0:-2]),gid[-2],gid[-1]]
					if gid[2].isdigit():
						gid[2] = int(gid[2])
						ids[gid[2]]=[gid[0],True]
			del gids
		if active_group_id:
			if self.group != None:
				return [str(self.group[0])]
		elif all_group_ids:
			return [str(gid) for gid in list(ids.keys())]
		for gid, name in ids.items():
			response.append({True:"g",False:"u"}[name[1]] + "id="+str(gid)+"(" + str(name[0]) + ")")
		return response

	def groupadd(self,args=[]):
		response = []
		unique_id = True
		non_unique = False
		key = self.get_env_vars("groupadd",True)
		system = False
		group_name = False
		if len(args) > 0:
			get_next_parameter = [False,False]
			for arg in args:
				if get_next_parameter[0]:
					get_next_parameter[0] = False
					if get_next_parameter[1] in ["-g","--gid"]:
						if arg.isdigit():
							arg = int(arg)
							if arg > 0:
								unique_id = arg
						return ["groupadd: invalid value of '" + arg + "' for " + get_next_parameter[1] + " parameter"] 
					elif get_next_parameter[1] == "-K":
						if type(key) != dict:
							key = {}
						if len(get_next_parameter) != 3:
							if not arg.startswith("-"):
								get_next_parameter[0] = True
								get_next_parameter.append(arg)
								continue
						else:
							key[get_next_parameter[2]] = arg
							del get_next_parameter[2]
							continue
				if arg.startswith("-"):
					if arg in ["-g","--gid"]:
						unique_id = True
						get_next_parameter = [True,arg]
					elif arg in ["-o","--non-unique"]:
						non_unique = False
					elif arg in ["-K","--key"]:
						key = True
						get_next_parameter = [True,"-K"]
					elif arg in ["-r","--system"]:
						key = self.get_env_vars("login",True)
						try:
							key["GID_MIN"] = key["SYS_GID_MIN"]
							key["GID_MAX"] = key["SYS_GID_MAX"]
						except:
							pass
						system = True
					else:
						raise ValueError(arg)
				elif group_name == False:
					group_name = arg
				else:
					raise ValueError(arg)
			for required in ["GID_MIN","GID_MAX","MAX_MEMBERS_PER_GROUP"]:
				if required not in key.keys():
					raise ReferenceError(required)
				else:
					if key[required].isdigit():
						key[required] = int(key[required])
						if key[required] < 0:
							raise ReferenceError(required)
			if len(group_name.split()) > 1:
				return ["groupadd: group name must not contain any whitespace"]
			current_directory = self.get_cwd()
			self.change_directory(["/"])
			if not os.path.exists(self.base_directory + "/etc/group"):
				group_data = []
			else:
				group_data = self.concatenate(["/etc/group"])
			groups = {}
			for group_data_ids in group_data:
				group_data_ids = group_data_ids.split(":")
				group_data_ids.pop()
				if len(group_data_ids) >= 3:
					group_relative_data = [":".join(group_data_ids[0:-2]),group_data_ids[-2],group_data_ids[-1]]
					if group_relative_data[2].isdigit():
						group_relative_data[2] = int(group_relative_data[2])
						if not group_relative_data[2] in groups.keys():
							groups[group_relative_data[2]] = [group_relative_data[0],group_relative_data[1]]
			if unique_id not in [True,False]:
				if non_unique:
					if unique_id > key["GID_MAX"] or unique_id < key["GID_MIN"]:
						return ["groupadd: '" + unique_id + "' is out of the bounds of " + str(key["GID_MIN"]) + " and " + str(key["GID_MAX"])]
				else:
					return ["groupadd: required permission to add a group with a non-unique GID, try '-o'"]
				if unique_id in groups.keys:
					if force:
						gid_generations = 0
						while unique_id in [True,False] or unique_id in list(groups.keys()):
							try:
								unique_id = randint(key["GID_MIN"],key["GID_MAX"]+1)
							except:
								gid_generations += 1
								if gid_generations == 2:
									return ["groupadd: the only possible GID from provided boundaries already exists - " + key["GID_MIN"]]
								unique_id = key["GID_MIN"]
					else:
						return ["groupadd: the provided GID is already associated to another user group"]
			else:
				gid_generations = 0
				while unique_id in [True,False] or unique_id in list(groups.keys()):
					unique_id = randint(key["GID_MIN"],key["GID_MAX"]+1)
					try:
						pass
					except:
						gid_generations += 1
						if gid_generations == 2:
							return ["groupadd: the only possible GID from provided boundaries already exists - " + key["GID_MIN"]]
						unique_id = key["GID_MIN"]
			base_group_name = group_name
			group_iteration = 1
			while group_name in groups.values():
				group_iteration += 1
				group_name = base_group_name + str(group_iteration)
			groups[unique_id] = [group_name,{True:"x",False:key["MAX_MEMBERS_PER_GROUP"]}[key["MAX_MEMBERS_PER_GROUP"] == 0]]
			group_string = []
			for group_id in groups.keys():
				group_string.append(groups[group_id][0] + ":"+ groups[group_id][1] + ":" + str(group_id) + ":")
			with open(self.base_directory+"/etc/group","w") as grouping:
				grouping.write("\n".join(group_string))
			return unique_id
		else:
			return ["groupadd: expected a group name or id to be provided"]
	
	def get_cwd(self,args=[]):
		self.dir
		if self.dir == "/":
			return "/"
		return self.dir

	def get_display_cwd(self,args=[]):
		display_dir = self.directory_restrict(self.dir)
		display_dir=display_dir[1]
		if display_dir == "/" or len(display_dir) == 0:
			return "/"
		return display_dir.replace("//","/")

	def ls(self,args=[]):
		files = [".",".."]
		reverse = False
		show_dirs = False
		show_all = False
		comma = False
		qoutation = False
		qouting_literal = False
		color = False
		if len(args) >= 1:
			for arg in args:
				if color == None:
					color = arg
				elif arg in ["-a","--all"]:
					show_all = True
				elif arg in ["-A","--almost-all"]:
					files = []
				elif arg == "--color":
					color = None
				elif arg in ["-r","--reverse"]:
					reverse = True
				elif arg == "-p":
					show_dirs = True
				elif arg == "-m":
					comma = True
				elif arg in ["-q","--quote-name"]:
 					qoutation = True
				elif arg in ["-n","--literal"]:
					qouting_literal = True
				else:
					raise ValueError(arg)
		if color == None:
			color = True
		if color not in [True,False,"always","never","auto"]:
			raise ValueError("--color="+str(color))
		files = files + os.listdir(self.get_cwd())
		list_files = []
		for x in range(len(files)):
			if not show_all:
				if files[x][0] == ".":
					continue
			if not qoutation and not qouting_literal:
				if len(files[x].split(" ")) > 1:
					files[x] = "'" + files[x] + "'"
			if os.path.isdir(self.dir_abspath(self.get_cwd()+"/"+files[x])):
				files[x] = {True:"\033[1;34m",False:""}[color in [True,"always","auto"]] + files[x] + {True:"\033[0m",False:""}[color in [True,"always","auto"]]
				if show_dirs:
					files[x] = files[x] + "/"
			if qoutation:
				files[x] = "\"" + files[x] + "\""
			list_files.append(files[x])
			if comma and len(list_files) > 0:
				list_files[len(list_files) - 1] = list_files[len(list_files) - 1] + ","
		if reverse:
			list_files.reverse()
		return list_files

	def get_hostname(self,args=[]):
		default = "computer"
		current_directory = self.get_display_cwd()
		if self.stable:
			self.change_directory(["/etc"])
		else:
			self.change_directory([self.base_directory + "/etc"])
		if "hostname" in self.ls(["-A","--color","never"]):
			hostname = self.concatenate(["hostname"])
			if len(hostname) == 1:
				if hostname[0].strip() != "":
					default = hostname[0]
		self.change_directory([current_directory])
		return default.replace(" ","-")

	def who_am_i(self,args=[]):
		default = "user"
		if self.user != None:
			return self.user
		return default

	def uname(self,args=[]):
		response = []
		kernel_name = False
		nodename = False
		kernel_release = False
		kernel_version = False
		for arg in args:
			if arg in ["-s","--kernel-name"]:
				kernel_name = True
			elif arg in ["-n","--nodename"]:
				nodename = True
			elif arg in ["-r","--kernel-release"]:
				kernel_release = True
			elif arg in ["-v","--kernel-version"]:
				kernel_version = True
			elif arg in ["-a","--all"]:
				kernel_name = True
				nodename = True
				kernel_release = True
				kernel_version = True
			else:
				raise ValueError(arg)
		if not kernel_version and not kernel_release and not nodename and not kernel_name:
			kernel_name = True
		if kernel_name:
			response.append("MicroPython")
		if nodename:
			response.append(self.get_hostname([]))
		if kernel_version:
			response.append("#" + str(version.__version__) + "-" + str(version.__build__) + " " + self.pretty_time(version.__time__))
		if kernel_release:
			if kernel_version:
				delimiters = ("(",")")
			else:
				delimiters = ("","")
			response.append(delimiters[0]+str(version.__release__)+delimiters[1])
		return response

	def move(self,args=[]):
		files = []
		for arg in args:
			if arg.startswith("-"):
				if arg not in ["-r","-R","--recursive","-v","--verbose"]:
					raise ValueError(arg)
			else:
				files.append(arg)
		if len(files) != 2:
			if len(files) == 0:
				return ["mv: missing file operand"]
			if len(files) == 1:
				return ["mv: missing destination file operand after '" + files[0] + "'"]
			elif len(files) > 2:
				return ["mv: too many arguments"]
		return self.copy(args,True)

	def copy(self,args=[],remove=False):
		verbose = False
		recursive = False
		copy_loc = []
		prepend_output = ""
		joint_command_type = {True:"cp",False:"mv"}[not remove]
		if remove:
			prepend_output = "renamed "
			joint_command_type = "mv"
		if len(args) >= 1:
			for arg in args:
				if not arg.startswith("-"):
					copy_loc.append(arg)
				else:
					if arg in ["-v","--verbose"]:
						verbose = True
					elif arg in ["-r","-R","--recursive"]:
						recursive = True
					else:
						raise ValueError(arg)
		else:
			return [joint_command_type + ": missing operand"]
		response = []
		if len(copy_loc) == 0:
			return [joint_command_type + ": missing operand"]
		elif len(copy_loc) < 2:
			return [joint_command_type + ": missing destination file operand after " + copy_loc[0]]
		else:
			to_copy_tree = []
			current_active_directory = self.get_display_cwd()
			to_copy_base = copy_loc.pop(0)
			to_copy = [to_copy_base]
			to_copy_default = to_copy
			to_copy_iteration = 0
			file_count = 0
			while to_copy_iteration < len(to_copy):
				copy = to_copy[to_copy_iteration]
				copy_raw = copy
				copy = self.directory_restrict(self.dir_abspath(self.base_directory + {True:"",False:self.get_display_cwd()+"/"}[copy.startswith("/")] + copy).replace("//","/"))[1]
				to_copy_iteration += 1
				self.change_directory([current_active_directory])
				if not copy.startswith("/"):
					copy = current_active_directory + {True:"",False:"/"}[current_active_directory.endswith("/")] + copy
				if copy.endswith("*"):
					if copy_raw == to_copy_base:
						to_copy_base = copy.rstrip("*")
					copy = copy.rstrip("*")
					if self.change_directory([copy]) == None:
						if to_copy[to_copy_iteration-1] in to_copy_default:
							for x in range(len(to_copy_default)):
								if to_copy_default[x] == to_copy[to_copy_iteration-1]:
									to_copy_default[x] = copy
									break
						to_copy_tree_sub_rel = self.ls(["-A","--color","never"])
						for x in range(len(to_copy_tree_sub_rel)):
							if copy+to_copy_tree_sub_rel[x] not in to_copy:
								to_copy.insert(to_copy_iteration+x,copy+to_copy_tree_sub_rel[x])
						to_copy_iteration -=1
						del to_copy[to_copy_iteration]
						continue
					else:
						response.append(joint_command_type + ": cannot copy '" + to_copy[to_copy_iteration-1] + "' as no file or directory exists")
						to_copy_iteration -= 1
						del to_copy[to_copy_iteration]
						continue
				to_copy_tree_sub = [copy,self.change_directory([copy]) == None]
				if not to_copy_tree_sub[1]:
					file_count += 1
				if to_copy_tree_sub[1]:
					if not recursive:
						response.append(joint_command_type + ": cannot copy '" + to_copy[to_copy_iteration-1] + "' as it is a directory")
						to_copy_iteration -= 1
						del to_copy[to_copy_iteration]
						continue
					to_copy_tree_sub_rel = [ 
						self.directory_restrict(os.path.join(parent, name))[1]
						for (parent, subdirs, files) in os.walk(self.base_directory+copy)
						for name in files + subdirs
					]
					to_copy_tree_sub_rel_raw = to_copy_tree_sub_rel
					to_copy_tree_sub_rel = []
					for path in to_copy_tree_sub_rel_raw:
						if path[-3:] != "/.." and path[-2:] != "/.":
							to_copy_tree_sub_rel.append(path)
					del to_copy_tree_sub_rel_raw
					if to_copy_tree_sub_rel != [] and not recursive:
						response.append(joint_command_type + ": cannot copy '" + to_copy[to_copy_iteration-1] + "' as it is a directory")
						to_copy_iteration -= 1
						del to_copy[to_copy_iteration]
						continue
					if to_copy[to_copy_iteration-1] in to_copy_default:
						for x in range(len(to_copy_default)):
							if to_copy_default[x] == to_copy[to_copy_iteration-1]:
								to_copy_default[x] = copy
								break
					for x in range(len(to_copy_tree_sub_rel)):
						if to_copy_tree_sub_rel[x] not in to_copy:
							to_copy.insert(to_copy_iteration+x,to_copy_tree_sub_rel[x])
				to_copy_tree.append(to_copy_tree_sub + [("/"+"/".join(to_copy_tree_sub[0].split("/")[0:-1])).replace("//","/")])

			self.change_directory([current_active_directory])
			if len(to_copy_tree) == 0:
				return response
			to_copy_default = [{True:"/",False:to_copy_default_loc.rstrip("/")}[to_copy_default_loc.rstrip("/") == "" and self.change_directory([current_active_directory])==None] for to_copy_default_loc in to_copy_default if self.change_directory([to_copy_default_loc]) == None]
			self.change_directory([current_active_directory])
			to_copy_tree = sorted(to_copy_tree)
			base_copy = None
			copy_directories = []
			to_copy_tree = [x for i, x in enumerate(to_copy_tree) if i == to_copy_tree.index(x)]
			to_copy_base = self.directory_restrict(self.dir_abspath(self.base_directory + {True:"",False:self.get_display_cwd()+"/"}[to_copy_base.startswith("/")] + to_copy_base).replace("//","/"))[1]
			for send_to in copy_loc:
				send_to_raw = send_to
				send_to = ({True:"",False:self.get_display_cwd()+"/"}[send_to.startswith("/")] + send_to).replace("//","/")
				if file_count == 1 and file_count == len(to_copy):
					to_copy = to_copy[0]
					to_copy_raw = to_copy
					to_copy = self.dir_abspath({True:"",False:self.get_display_cwd()+"/"}[to_copy.startswith("/")] + to_copy)
					if self.link([to_copy,send_to]) == None:
						if remove:
							if self.unlink([to_copy]) != None:
								response.append("mv: unable to remove original file of '" + to_copy + "'")
						if verbose:
							response.append("'" + to_copy_raw + "' 1-> '" + send_to_raw + "'")
					else:
						response.append("'" + to_copy_raw + "' -> FAILED")
				else:
					base_change = len(to_copy_base)
					to_copy = sorted(to_copy)
					send_to = send_to.replace("//","/")
					send_to_base = self.create_directory([send_to,"-p"])
					send_to_base = send_to_base in [[],["mkdir: cannot create directory '" + send_to.rstrip("/") + "' as directory exists"]]
					for copy in to_copy:
						copy_abs_raw = copy
						copy = "/".join([send_to,copy[base_change:]]).replace("//","/")
						if self.change_directory([copy_abs_raw]) == None:
							if remove:
								copy_directories.append(copy_abs_raw)
							suc = self.create_directory([copy])
							if len(suc) == 0 or (copy.rstrip("/") == send_to.rstrip("/") and send_to_base):
								if verbose:
									response.append("'" + copy_abs_raw + "' -> '" + copy + "'")
							elif suc == ["mkdir: cannot create directory '" + copy.rstrip("/") + "' as directory exists"]:
								if verbose:
									response.append("'" + copy_abs_raw + "' -> IGNORED")
							else:
								response.append("'" + copy_abs_raw + "' -> FAILED")
						elif self.link([copy_abs_raw,copy]) == None:
							if remove:
								if self.unlink([copy_abs_raw]) != None:
									response.append("mv: unable to remove original file of '" + copy_abs_raw + "'")
							if verbose:
								response.append("'" + copy_abs_raw + "' -> '" + copy + "'")
						else:
							response.append("'" + copy_abs_raw + "' -> FAILED")
			copy_directories = sorted(copy_directories,reverse=True)
			for directory in copy_directories:
				self.remove_directory([directory])
			self.change_directory([current_active_directory])
			return response

	def concatenate(self,args=[]):
		cat_values = []	
		operation_to_file = []
		output_type = False
		line_count = False
		end_of_line = False
		show_tabulations = False
		squeeze_blanks = False
		if len(args) >= 1:
			get_next_output = False
			output_type_type_verification = -1
			for arg in args:
				if arg.startswith("-"):
					if arg in ["-n","--number"]:
						line_count = True
					elif arg in ["-e","--show-ends"]:
						end_of_line = True
					elif arg in ["-t","--show-tabs"]:
						show_tabulations = True
					elif arg in ["-s","--squeeze-blank"]:
						squeeze_blanks = True
					else:
						raise ValueError(arg)
				else:
					cat_values.append(arg)
			if get_next_output:
				if len(operation_to_file[-1][1]) == 0:
					return ["cat: syntax error where output was expected"]
		response = []
		output_error_stream = []
		output_stream = []
		previous_line = None
		if len(cat_values) == 0:
			while True:
				try:
					input_stream_buffer = self.input_method(0)
				except EOFError:
					break
				if show_tabulations:
					input_stream_buffer = input_stream_buffer.replace("\t","^I")
				if end_of_line:
					input_stream_buffer = input_stream_buffer + "$"
				if not (squeeze_blanks and previous_line == input_stream_buffer and len(output_stream) > 0 and len(input_stream_buffer) >= 0):
					if squeeze_blanks:
						previous_line = input_stream_buffer
				output_stream.append(input_stream_buffer)
		else:
			for file in cat_values:
				file_relative = file
				if file.startswith("/"):
					file = self.base_directory + file
				else:
					file = self.get_cwd() + "/" + file
				#file = self.dir_abspath(file)
				if not os.path.isfile(file):
					output_error_stream.append("cat: unable to use file '" + file_relative + "' for input stream as it does not exists")
				else:
					try:
						with open(file,"rb") as output_file:
							for line in output_file.readlines():
								try:
									line = line.decode("UTF-8")
								except:
									try:
										line = line.decode("ascii")
									except:
										raise Exception("Unknown encoding")
								line = line.rstrip()
								if show_tabulations:
									line = line.replace("\t","^I")
								if end_of_line:
									line = line + "$"
								if not (squeeze_blanks and previous_line == line and len(output_stream) > 0 and len(line) >= 0):
									if squeeze_blanks:
										previous_line = line
									output_stream.append(line)
					except Exception as e:
						output_stream = []
						output_error_stream.append("cat: unable to read the file '" + file_relative + "' as the encoding type is not dynamically supported")
		total_lines = len(output_stream)
		total_lines_character_size = len(str(total_lines))
		for line_num in range(total_lines):
			if line_count:
				response.append(((total_lines_character_size - len(str(line_num + 1)) + 1) * " ") + str(line_num + 1) + " " + output_stream[line_num])
			else:
				response.append(output_stream[line_num])
		response.extend(output_error_stream)
		return response

	def tail(self,args=[]):
		return self.head(args,True)

	def head(self, args=[],reverse=False):
		total_lines = 10
		get_next_parameter = [False,False]
		response = []
		files = []
		joint_command_type = "head"
		if reverse:
			joint_command_type = "tail"
		for arg in args:
			if get_next_parameter[0]:
				get_next_parameter[0] = False
				if get_next_parameter[1] == "-n":
					if arg.isdigit():
						arg = int(arg)
						if arg > 0:
							total_lines = arg
							continue
				response.append(joint_command_type + ": invalid number of lines '" + arg + "'")
				continue
			if arg.startswith("-"):
				if arg in ["-n","--lines"]:
					get_next_parameter = [True,arg]
				else:
					raise ValueError(arg)
			else:
				files.append(arg)
		file_iteration = 0
		for file in files:
			file_raw_location = file
			if not file.startswith("/"):
				file = self.dir_abspath(self.get_display_cwd() + "/" + file)
				file_raw_location = file
				file = self.base_directory + file
			file = self.dir_abspath(file)
			if not os.path.isfile(file):
				if os.path.isdir(file):
					response.append(joint_command_type + ": unable to read '" + file_raw_location + "' as it is a directory")
				else:
					response.append(joint_command_type + ": unable to read '" + file_raw_location + "' as no file or directory exists")
			else:
				file_contents = self.concatenate([file_raw_location])
				if len(files) > 1:
					if file_iteration >= 1:
						response.append("")
					response.append("==> " + file_raw_location + " <==")
				if reverse:
					response.extend(file_contents[-total_lines:])
				else:
					response.extend(file_contents[:total_lines])
			file_iteration += 1
		return response

	def change_directory(self, args=[]):
		if len(args) > 1:
			return "cd: too many arguments"
		elif len(args) == 0:
			return
		args = args[0]
		if args.startswith("/"):
			directory = self.dir_abspath(args)
		else:
			current_directory = self.get_display_cwd()
			if current_directory != "/":
				current_directory = current_directory + "/"
			directory = self.dir_abspath(current_directory + args)
		if args.startswith("/"):
			directory = self.base_directory + args
		else:
			directory = os.path.normpath(self.get_cwd() + "/" + args)
		directory = self.directory_restrict(directory)[0]
		if not self.stable:
			directory = args
		if os.path.isdir(directory):
			self.set_cwd(args)
		else:
			return "cd: " + args + " is not a directory"

	def create_directory(self, args=[]):
		verbose = False
		create_directory_parents = False
		dir_listings = []
		if len(args) >= 1:
			for arg in args:
				if not arg.startswith("-"):
					dir_listings.append(arg)
				else:
					if arg in ["-v","--verbose"]:
						verbose = True
					elif arg in ["-p","--parents"]:
						create_directory_parents = True
					else:
						raise ValueError(arg)
		else:
			return ["mkdir: missing operand"]
		current_base_dir = self.get_display_cwd().split("/")
		response = []
		if len(dir_listings) == 0:
			return ["mkdir: missing operand"]
		for dir_new in dir_listings:
			self.change_directory(["/".join(current_base_dir)])
			dir_new_default_string = dir_new
			if dir_new_default_string[0] != "/":
				dir_new_default_string = ("/" + "/".join(current_base_dir) + "/" + dir_new_default_string).replace("//","/")
			dir_new_default_string = os.path.normpath(dir_new_default_string).split("/")
			dir_string = ""
			dir_deviate_sub_name = ""
			dir_deviate_destination_name = ""
			dir_child_iteration = 0
			small_relative_dir_creation = [""]
			dir_string_name = "/"
			dir_scouse_iteration = 1
			for directory_persist in dir_new_default_string:
				dir_string_parent_name = dir_string_name
				dir_string_name = (dir_string_name + directory_persist + "/").replace("//","/")
				if directory_persist == "":
					self.change_directory(["/"])
				elif self.change_directory([directory_persist]) != None:
					if create_directory_parents and len(dir_new_default_string) != dir_scouse_iteration:
						try:
							os.mkdir(self.base_directory + dir_string_name)
							if verbose:
								response.append("mkdir: created directory '" + dir_string_name.rstrip("/") + "'")
						except OSError as e:
							response.append("mkdir: failed to create the directory '" + dir_string_name.rstrip("/") + "'")
							continue
					elif len(dir_new_default_string) == dir_scouse_iteration:
						try:
							os.mkdir(self.base_directory + dir_string_name)
							if verbose:
								response.append("mkdir: created directory '" + dir_string_name.rstrip("/") + "'")
						except OSError as e:
							response.append("mkdir: failed to create the directory '" + dir_string_name.rstrip("/") + "'")
							continue
					else:
						response.append("mkdir: cannot create directory '" + dir_string_name.rstrip("/") + "' as no file or directory exists")
						continue
				elif len(dir_new_default_string) == dir_scouse_iteration:
					response.append("mkdir: cannot create directory '" + dir_string_name.rstrip("/") + "' as directory exists")
				dir_scouse_iteration += 1
		self.change_directory(["/".join(current_base_dir)])
		return response

	def link(self, files=[]):
		if len(files) >= 1:
			if len(files) == 1:
				return "link: missing operand after '" + files[0] + "'"
			elif len(files) == 2:
				files_raw = [files][0]
				if self.stable:
					files[0] = ((self.base_directory+({True:"",False:(self.get_display_cwd() + "/").replace("//","/")}[files[0].startswith("/")])).replace("//","/") + "/" + files[0]).replace("//","/")
					files[1] = ((self.base_directory+({True:"",False:(self.get_display_cwd() + "/").replace("//","/")}[files[1].startswith("/")])).replace("//","/") + "/" + files[1]).replace("//","/")
				else:
					if not files[0].startswith("/"):
						files[0] = self.dir_abspath(files[0])
					if not files[1].startswith("/"):
						files[1] = self.dir_abspath(files[1])
				if os.path.exists(files[0]):
					if os.path.isfile(files[0]):
						if not files[1].startswith("/"):
							files[1] = self.dir_abspath(files[1])
						if os.path.exists(files[1]):
							return "link: cannot create link from '" + files_raw[0] + "' as the file '" + files_raw[1] + "' exists"
						else:
							if os.path.isdir(files[0]):
								self.create_directory([files[1],"-p"])
							else:
								with open(files[0],"rb") as source:
									with open(files[1],"wb") as destination:
										while True:
											piece = source.read(self.buffer)
											if len(piece) == 0:
												break
											else:
												destination.write(piece)
							return None
					elif os.path.isdir(files[0]):
						return "link: cannot create link from '" + files_raw[0] + "' to '" + files_raw[1] + "'"
				else:
					return "link: cannot create link from '" + files_raw[0] + "' to '" + files_raw[1] + "' as no file exists"
			else:
				return "link: extra operand '" + files[2] + "'"
		else:
			return "link: missing operand"

	def unlink(self,file=[]):
		response = []
		if len(file) > 1:
			return "unlink: extra operand '" + file[1] + "'"
		elif len(file) == 0:
			return "unlink: missing operand"
		else:
			file = file[0]
			file_raw = file
			if self.stable:
				file = ((self.base_directory+({True:"",False:(self.get_display_cwd() + "/").replace("//","/")}[file.startswith("/")])).replace("//","/") + "/" + file).replace("//","/")
			else:
				if not file.startswith("/"):
					file = self.dir_abspath(file)
			if os.path.exists(file):
				if os.path.isfile(file):
					os.unlink(file)
					return None
				else:
					return "unlink: cannot unlink '" + file_raw + "' as it is a directory"
			else:
				return "unlink: cannot unlink '" + file_raw + "' as no file or directory"

	def remove(self,args=[]):
		force = False
		prompt_every = False
		prompt_3_plus = False
		recursive = False
		directory = False
		verbose = False
		to_remove = []
		if len(args) >= 1:
			for arg in args:
				if not arg.startswith("-"):
					to_remove.append(arg)
				else:
					if arg in ["-v","--verbose"]:
						verbose = True
					elif arg in ["-f","--force"]:
						force = True
						prompt_every = False
						prompt_3_plus = False
					elif arg == "-i" and not force:
						prompt_every = True
					elif arg == "-I" and not force:
						prompt_3_plus = True
					elif arg in ["-r","-R","--recursive"]:
						recursive = True
					elif arg in ["-d","--dir"]:
						directory = True
					else:
						raise ValueError(arg)
		else:
			return ["rm: missing operand"]
		response = []
		if len(to_remove) == 0:
			return ["rm: missing operand"]
		else:
			to_remove_tree = []
			current_active_directory = self.get_display_cwd()
			to_remove_iteration = 0
			to_remove_default = list(to_remove)
			while to_remove_iteration < len(to_remove):
				self.change_directory([current_active_directory])
				remove = to_remove[to_remove_iteration]
				remove = self.directory_restrict(self.dir_abspath(self.base_directory + {True:"",False:self.get_display_cwd()+"/"}[remove.startswith("/")] + remove).replace("//","/"))[1]
				to_remove_iteration += 1
				if not remove.startswith("/"):
					remove = current_active_directory + {True:"",False:"/"}[current_active_directory.endswith("/")] + remove
				if remove.endswith("*"):
					remove = remove.rstrip("*")
					if self.change_directory([remove]) == None:
						if to_remove[to_remove_iteration-1] in to_remove_default:
							for x in range(len(to_remove_default)):
								if to_remove_default[x] == to_remove[to_remove_iteration-1]:
									to_remove_default[x] = remove
									break
						to_remove_tree_sub_rel = self.ls(["-A","--color","never"])
						for x in range(len(to_remove_tree_sub_rel)):
							to_remove.insert(to_remove_iteration+x,remove+to_remove_tree_sub_rel[x])
						continue
					else:
						response.append("rm: cannot remove '" + to_remove[to_remove_iteration-1] + "' as no file or directory exists")
				to_remove_tree_sub = [remove,self.change_directory([remove]) == None]
				if to_remove_tree_sub[1]:
					if not recursive and not directory:
						response.append("rm: cannot remove '" + to_remove[to_remove_iteration-1] + "' as it is a directory")
						continue
					to_remove_tree_sub_rel = [ 
						self.directory_restrict(os.path.join(parent, name))[1]
						for (parent, subdirs, files) in os.walk(self.base_directory+remove)
						for name in files + subdirs
					]
					to_remove_tree_sub_rel_raw = to_remove_tree_sub_rel
					to_remove_tree_sub_rel = []
					for path in to_remove_tree_sub_rel_raw:
						if path[-3:] != "/.." and path[-2:] != "/.":
							to_remove_tree_sub_rel.append(path)
					del to_remove_tree_sub_rel_raw
					if to_remove_tree_sub_rel != [] and directory and not recursive:
						response.append("rm: cannot remove '" + to_remove[to_remove_iteration-1] + "' as it is a directory")
						continue
					if to_remove[to_remove_iteration-1] in to_remove_default:
						for x in range(len(to_remove_default)):
							if to_remove_default[x] == to_remove[to_remove_iteration-1]:
								to_remove_default[x] = remove
								break
					for x in range(len(to_remove_tree_sub_rel)):
						to_remove.insert(to_remove_iteration+x,to_remove_tree_sub_rel[x])
				to_remove_tree.append(to_remove_tree_sub + [("/"+"/".join(to_remove_tree_sub[0].split("/")[0:-1])).replace("//","/")])
			self.change_directory([current_active_directory])
			to_remove_default = [{True:"/",False:to_remove_default_loc.rstrip("/")}[to_remove_default_loc.rstrip("/") == "" and self.change_directory([current_active_directory])==None] for to_remove_default_loc in to_remove_default if self.change_directory([to_remove_default_loc]) == None]
			self.change_directory([current_active_directory])
			if len(to_remove_tree) > 3 and prompt_3_plus:
				if self.input_method(1,"rm: remove " + str(len(to_remove_tree)) + " arguments recursively? ")[0] != "y":
					return None
			to_remove_tree = sorted(to_remove_tree,reverse=True)
			base_remove = None
			remove_directories = []
			current_directory_del = None
			to_remove_tree = [x for i, x in enumerate(to_remove_tree) if i == to_remove_tree.index(x)]
			for x in range(2):
				to_remove_iteration = 0
				while to_remove_iteration < len(to_remove_tree):
					if x == 1:
						to_remove = [False,False,""]
					else:
						to_remove = to_remove_tree[to_remove_iteration]
					if to_remove[1] and x == 0:
						if not to_remove[0] in to_remove_default:
							if prompt_every:
								self.change_directory([to_remove[0]])
								if self.ls(["-A"]) != []:
									if self.input_method(1,"rm: descend into directory '" + str(to_remove[0]) + "'? ")[0] != "y":
										self.change_directory([to_remove[0]])
										continue
								self.change_directory([current_active_directory])
						if to_remove[0].split("/") not in remove_directories:
							remove_directories.append(to_remove[0].split("/"))
					else:
						remove_directory_iteration = 0
						while remove_directory_iteration < len(remove_directories):
							remove_directory = remove_directories[remove_directory_iteration]
							if to_remove[2].split("/")[0:len(remove_directory)] != remove_directory[0:len(to_remove)] or x == 1 or remove_directory in to_remove_default:
								if prompt_every and not directory and remove_directory not in to_remove_default:
									if self.input_method(1,"rm: remove directory '" + "/".join(remove_directory) + "'? ")[0] != "y":
										del remove_directories[remove_directory_iteration]
										del to_remove_tree[to_remove_iteration]
										continue
								operation_success = self.remove_directory(["/".join(remove_directory)]) == []
								if verbose or not operation_success:
									response.append({True:"removed",False:"rm: cannot remove directory"}[operation_success] + " '" + "/".join(remove_directory) + "'")
								del remove_directories[remove_directory_iteration]
								continue
							remove_directory_iteration+=1
						if x == 0:
							if prompt_every:
								if self.input_method(1,"rm: remove regular " + {True:"empty ",False:""}[len(self.concatenate([to_remove[0]])) == 0] + "file '" + to_remove[0] + "'? ")[0] != "y":
									continue
							operation_success = self.unlink([to_remove[0]]) == None
							if verbose or not operation_success:
								response.append({True:"removed",False:"rm: cannot remove"}[operation_success] + " '" + to_remove[0] + "'")
					to_remove_iteration += 1
				remove_directories = sorted(remove_directories,reverse=True)
			return response

	def remove_directory(self,args=[]):
		verbose = False
		delete_directory_parent = False
		dir_listings = []
		if len(args) >= 1:
			for arg in args:
				if not arg.startswith("-"):
					if arg.startswith("/"):
						dir_listings.append(arg)
					else:
						dir_listings.append((self.get_display_cwd() + "/" + arg).replace("//","/"))
				else:
					if arg in ["-v","--verbose"]:
						verbose = True
					elif arg in ["-p","--parents"]:
						delete_directory_parent = True
					else:
						raise ValueError(arg)
		else:
			return ["rmdir: missing operand"]
		if len(dir_listings) == 0:
			return ["rmdir: missing operand"]
		response = []
		current_base_dir = self.get_display_cwd().split("/")[1:]
		for dir_del in dir_listings:
			if dir_del.startswith("/"):
				is_root = "/"
			else:
				is_root = ""
			dir_delete_default_string = dir_del
			dir_del_default_string = dir_delete_default_string.split("/")[1:]
			if current_base_dir == dir_del_default_string:
				response.append("rmdir: failed to remove '" + self.get_display_cwd().split("/")[-1] + "' as the current directory cannot be deleted")
				continue
			dir_string = ""
			dir_deviate_sub_name = ""
			dir_deviate_destination_name = ""
			dir_child_iteration = 0
			small_relative_dir_creation = [""]
			for dir_del_sub_name in dir_del_default_string:
				dir_base_use = False
				dir_del_sub_name_generation_continue = True
				if dir_child_iteration < len(current_base_dir):
					dir_base_use = True
				if dir_base_use:
					if dir_del_sub_name == current_base_dir[dir_child_iteration]:
						dir_string = dir_string + "/" + dir_del_sub_name
						dir_del_sub_name_generation_continue = False
				if dir_del_sub_name_generation_continue:
					if dir_child_iteration == len(dir_del_default_string) - 1:
						dir_deviate_destination_name = dir_del_sub_name
					else:
						dir_deviate_sub_name = dir_deviate_sub_name + "/" + dir_del_sub_name
					if len(small_relative_dir_creation) > 1:
						small_relative_dir_creation.append(small_relative_dir_creation[-1] + "/" + dir_del_sub_name)
					else:
						small_relative_dir_creation = [None,dir_del_sub_name]
				dir_child_iteration+=1
			del_dir = dir_string.split("/")[1:]
			small_relative_dir_creation = small_relative_dir_creation[1:]
			if self.change_directory(["/"+"/".join(dir_del_default_string)]) == None:
				small_relative_dir_creation.reverse()
				directory_parent_naming = []
				dir_del_tree = dir_del.split("/")[1:]
				for directory in dir_del_tree:
					if len(directory_parent_naming) == 0:
						directory_parent_naming.append([directory])
					else:
						directory_parent_naming.append(directory_parent_naming[-1] + [directory])
				directory_parent_naming.reverse()
				dir_del_tree.reverse()
				dir_deletion_iteration = 0
				for dir_del_parent in dir_del_tree:
					directory_contents = self.ls(["-A","--color","never"])
					if directory_contents != []:
						response.append("rmdir: failed to remove '" + is_root + small_relative_dir_creation[dir_deletion_iteration] + "' as directory is not empty")
					else:
						self.change_directory([".."])
						if verbose:
							response.append("rmdir: removing directory '" + is_root + small_relative_dir_creation[dir_deletion_iteration] + "'")
						try:
							os.rmdir(self.get_cwd() + "/" + dir_del_parent)
						except OSError as e:
							response.append("rmdir: failed to remove '" + is_root + small_relative_dir_creation[dir_deletion_iteration] + "'")
					dir_deletion_iteration+=1
					if self.get_cwd() == self.dir_abspath(dir_string):
						break;
					elif not delete_directory_parent:
						break;
			else:
				if dir_del == "":
					dir_del = "/"
				else:
					dir_del = "/".join(small_relative_dir_creation)
				response.append("rmdir: failed to remove '" + dir_del + "' as no file or directory exists")
			self.change_directory(["/" + "/".join(current_base_dir)])
		current_base_dir = "/" + "/".join(current_base_dir)
		if self.get_cwd() != current_base_dir:
			self.change_directory([current_base_dir])
		return response

	def echo(self,args=[]):
		response = []
		newline = True
		escape_interpretation = False
		content = []
		for arg in args:
			if arg.startswith("-"):
				if arg == "-n":
					newline = False
				elif arg == "-e":
					escape_interpretation = True
				elif arg == "-E":
					escape_interpretation = False
				else:
					raise ValueError(arg)
			else:
				content.append(arg)
		for part in content:
			if escape_interpretation:
				part = part.split("\\")
				partition = 0
				while partition < len(part):
					inspect = part[partition]
					partition += 1
					if partition < len(part):
						if len(part[partition]) > 0:
							if part[partition][0] in ["\"","\'","f","n","r","t","v"]:
								base = part[partition][0]
								part[partition] = part[partition][1:]
								part[partition-1] = inspect + {"\"":"\"","\'":"\'","f":"\f","n":"\n","r":"\r","t":"\t","v":"\v"}[base] + part[partition]
								del part[partition]
								partition -= 1
				part = "\\".join(part)
			response.append(part)
		if len(response) == 0 and newline:
			response.append("")
		return response

	def touch(self,args=[]):
		files = args
		response = []
		if len(files) == 0:
			return ["touch: missing file operand"]
		for x in range(len(files)):
			raw_file_loc = files[x]
			files[x] = (self.base_directory + (self.dir_abspath({True:"",False:(self.get_display_cwd() + "/").replace("//","/")}[files[x].startswith("/")] + files[x]))).replace("//","/")
			if not os.path.exists(files[x]):
				with open(files[x], 'a') as to_touch:
					to_touch.write("")
		return response

	def alias(self,args=[]):
		response = []
		print_aliases = False
		if len(args) == 1:
			if args[0] in "-p":
				print_aliases = True
		aliases = []
		if not print_aliases:
			aliases_iteration = 0
			for arg in args:
				if parser_split(arg)[0] != arg:
					if len(aliases[aliases_iteration - 1]) == 2:
						raise ValueError(arg)
					arg = parser_split(arg)[0]
					aliases[aliases_iteration - 1].append(arg)
				else:
					aliases.append([arg])
					aliases_iteration += 1
			for alias_values in aliases:
				if len(alias_values) == 1:
					if alias_values[0] in self.alias_vars.keys():
						response.append("alias " + alias_values[0] + "='" + self.alias_vars[alias_values[0]] + "'")
					else:
						response.append("alias: " + alias_values[0] + ": not found")
				else:
					self.alias_vars[alias_values[0]] = alias_values[1]
					response.append("alias " + alias_values[0] + "='" + alias_values[1] + "'")
		if len(aliases) == 0:
			for alias_name, aliases in self.alias_vars.items():
				response.append("alias " + alias_name + "='" + aliases + "'")
		return response

	def unalias(self,args=[]):
		response = []
		if len(args) == 1:
			if args[0] in "-a":
				self.alias_vars = {}
				return []
		for alias in args:
			if alias in self.alias_vars.keys():
				del self.alias_vars[alias]
			else:
				response.append("unalias: " + alias + ": not found")
		return response

	def grep(self,args=[]):
		if self.pipe_in == None:
			return ["grep: missing piped input stream"]
		else:
			response = []
			line_count = False
			ignore_case = False
			quiet = False
			max_lines = -1
			search = None
			color = False
			invert = False
			get_next_parameter = [False,False]
			for arg in args:
				if get_next_parameter[0]:
					get_next_parameter[0] = False
					if get_next_parameter[1] == "-m":
						if arg.isdigit():
							arg = int(arg)
							if arg > 0:
								max_lines = arg
								continue
						response.append("grep: invalid number of lines '" + arg + "'")
						continue
				elif arg.startswith("-"):
					if arg in ["-c","--count"]:
						line_count = True
					elif arg in ["-i","--ignore-case"]:
						ignore_case = True
					elif arg in ["-m","--max-count"]:
						get_next_parameter = [True,"-m"]
					elif arg in ["-q","--quiet","--silent"]:
						quiet = True
					elif arg in ["--color","--colour"]:
						color = True
					elif arg in ["-v","--invert-match"]:
						invert = True
					else:
						raise ValueError(arg)
				elif parser_split(arg)[0] != arg:
					search = " ".join(parser_split(arg))
					continue
			if search == None:
				return ["grep: missing search parameter"]
			if ignore_case:
				search = search.lower()
			if type(self.pipe_in) != list:
				if type(self.pipe_in) == str:
					self.pipe_in = self.pipe_in.split(" ")
			for entry in self.pipe_in:
				actual_entry = entry
				if ignore_case:
					entry = entry.lower()
				if entry.find(search) >= 0 and invert:
					continue
				elif entry.find(search) < 0 and not invert:
					continue
				if quiet:
					return None
				if color:
					actual_entry = actual_entry.replace(search,"\033[1m\033[31m" + search + "\033[0m")
				response.append(actual_entry)
				if max_lines >= 0:
					if len(response) >= max_lines:
						break
			total_lines_character_size = len(response)
			if line_count:
				return [str(len(response))]
			return response
		return None

	def uniq(self,args=[]):
		if self.pipe_in == None:
			return ["uniq: missing piped input stream"]
		else:
			response = []
			count = False
			only_duplicates = False
			ignore_case = True
			only_unique = False
			for arg in args:
				if arg.startswith("-"):
					if arg in ["-c","--count"]:
						count = True
					elif arg in ["-d","--repeated"]:
						only_duplicates = True
					elif arg in ["-i","--ignore-case"]:
						ignore_case = True
					elif arg in ["-u","--unique"]:
						only_unique = True
					else:
						raise ValueError(arg)
				else:
					raise ValueError(arg)
			unique = []
			for line in self.pipe_in:
				unique_positional_list_loc = 0
				is_unique = True
				for entry in unique:
					if entry[1] == line:
						is_unique = False
						entry[0] += 1
						unique[unique_positional_list_loc] = entry
					if ignore_case:
						if entry[1].lower() == line.lower():
							is_unique = False
							entry[0] += 1
							unique[unique_positional_list_loc] = entry
					unique_positional_list_loc += 1
				if is_unique:
					unique.append([1,line])
			max_num = 0
			if count:
				for entry in unique:
					if entry[0] >= max_num:
						max_num = entry[0]
			for entry in unique:
				if only_unique:
					if entry[0] != 1:
						continue
				elif only_duplicates:
					if entry[0] <= 1:
						continue
				if count:
					response.append(" " + str(entry[0]) + ((len(str(max_num)) - len(str(entry[0])) + 1) * " ") + entry[1])
				else:
					response.append(entry[1])
		return response

	def sort(self,args=[]):
		if self.pipe_in == None:
			return ["sort: missing piped input stream"]
		else:
			response = self.pipe_in
			reverse = False
			ignore_case = False
			for arg in args:
				if arg in ["-r","--reverse"]:
					reverse = True
				elif arg in ["-f","--ignore-case"]:
					ignore_case = True
				else:
					raise ValueError(arg)
			if type(self.pipe_in) != list:
				if type(self.pipe_in) == str:
					response = self.pipe_in.split(" ")
			if ignore_case:
				response.sort(reverse = reverse, key=str.upper)
			else:
				response.sort(reverse = reverse)
			return response

	def clear(self,args=[]):
		raise SystemExit("clear")
		return None

	def wget(self,args=[]):
		response = []
		verbose = 1
		input_file = False
		locations = [False]
		tries = 20
		timeout = 9
		get_next_parameter = [False, False]
		if len(args) >= 1:
			for arg in args:
				if get_next_parameter[0]:
					get_next_parameter[0] = False
					if get_next_parameter[1] == "-t":
						if arg.isdigit():
							arg = int(arg)
							if arg > 0:
								tries = arg
								continue
					elif get_next_parameter[1] == "-i":
						input_file = arg
				elif arg.startswith("-"):
					if arg in ["-v","--verbose","-nv","--no-verbose"]:
						if arg in ["-v","--verbose"]:
							verbose = 2
						else:
							verbose = 0
					elif arg in ["-i","--input-file"]:
						get_next_parameter = [True,"-i"]
					elif arg in ["-t","--tries"]:
						get_next_parameter = [True,"-t"]
					else:
						raise ValueError(arg)
				elif locations == [False]:
					locations = [arg]
				else:
					return ["wget: cannot use '" + arg + "' as a source location as '" + locations[0] + "' has already been defined"]
		else:
			return ["wget: missing operand"]
		if input_file != False:
			if not input_file.startswith("/"):
				input_file = self.dir_abspath(input_file)
			if os.path.exists(input_file):
				if os.path.isfile(input_file):
					if locations == [False]:
						locations = []
					with open(input_file,"rb") as locations_from_file:
						for resource_location in locations_from_file.readlines():
							locations.append(str(resource_location.decode().rstrip()))
				else:
					return ["wget: input file does not exists"]
			else:
				return ["wget: input file does not exists"]
		default_file_mime_types = {"audio/aac":".aac","application/x-abiword":".abw","application/x-freearc":".arc","video/x-msvideo":".avi","application/vnd.amazon.ebook":".azw","application/octet-stream":".bin","image/bmp":".bmp","application/x-bzip":".bz","application/x-bzip2":".bz2","application/x-csh":".csh","text/css":".css","text/csv":".csv","application/msword":".doc","application/vnd.openxmlformats-officedocument.wordprocessingml.document":".docx","application/vnd.ms-fontobject":".eot","application/epub+zip":".epub","application/gzip":".gz","image/gif":".gif","text/html":".htm","text/html":".html","image/vnd.microsoft.icon":".ico","text/calendar":".ics","application/java-archive":".jar","image/jpeg":".jpeg","image/jpeg":".jpg","text/javascript":".js","application/json":".json","application/ld+json":".jsonld","audio/midi":".mid","audio/midi":".midi","text/javascript":".mjs","audio/mpeg":".mp3","video/mpeg":".mpeg","application/vnd.apple.installer+xml":".mpkg","application/vnd.oasis.opendocument.presentation":".odp","application/vnd.oasis.opendocument.spreadsheet":".ods","application/vnd.oasis.opendocument.text":".odt","audio/ogg":".oga","video/ogg":".ogv","application/ogg":".ogx","audio/opus":".opus","font/otf":".otf","image/png":".png","application/pdf":".pdf","application/php":".php","application/vnd.ms-powerpoint":".ppt","application/vnd.openxmlformats-officedocument.presentationml.presentation":".pptx","application/x-rar-compressed":".rar","application/rtf":".rtf","application/x-sh":".sh","image/svg+xml":".svg","application/x-shockwave-flash":".swf","application/x-tar":".tar","image/tiff":".tif","image/tiff":".tiff","video/mp2t":".ts","font/ttf":".ttf","text/plain":".txt","application/vnd.visio":".vsd","audio/wav":".wav","audio/webm":".weba","video/webm":".webm","image/webp":".webp","font/woff":".woff","font/woff2":".woff2","application/xhtml+xml":".xhtml","application/vnd.ms-excel":".xls","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":".xlsx","application/xml":".xml","application/vnd.mozilla.xul+xml":".xul","application/zip":".zip","video/3gpp":".3gp","video/3gpp2":".3g2","application/x-7z-compressed":".7z"}
		resource_iteration = 0
		wget_download_iteration = 0
		if locations == [False]:
			return ["wget: no URI was provided"]
		for location in locations:
			wget_download_iteration += 1
			resource_iteration += 1
			port = False
			if location.startswith("http://"):
				port = 80
			if port == False:
				response.append(self.output_method(0,"Unknown or unsupported protocol for the resource '" + location + "'"))
				response.append(self.output_method(0,"Supported protocol(s) include :"))
				response.append(self.output_method(0," - http://"))
			else:
				if verbose > 0:
					self.output_method(0,"--" + self.pretty_time(format_string="%Y-%m-%d %H:%M:%S") + "-- " + location)
				resolve_failure = False
				for x in range(tries):
					try:
						_, _, host, path = location.split("/", 3)
					except:
						try:
							_, _, host, path = (location + "/").split("/", 3)
						except:
							response.append(self.output_method(0,"Unable to parse the host URI for '" + location + "'"))
					if verbose > 0:
						if not resolve_failure or verbose == 2:
							self.output_method(1,"Resolving " + location + " (" + host + ")... ")
					try:
						addr = (socket.getaddrinfo(host, port)[0][-1],)
					except:
						if verbose > 1:
							response.append(self.output_method(0,"failed [" + str(x+1) + "]"))
						resolve_failure = True
						continue
					if resolve_failure and verbose > 1:
						self.output_method(0,"Resolving " + location + " (" + host + ")... ")
					resolve_failure = False
					if verbose > 0:
						try:
							ip = socket.getaddrinfo(host,23)[0][-1]
							if len(ip) / 4 == 4:
								set_ip = []
								for addr in range(len(ip)):
									if addr == 4:
										break
									set_ip.append(str(ip[addr+4]))
								ip = ".".join(set_ip)
								del set_ip
							else:
								ip = socket.inet_ntop(socket.AF_INET6,list(socket.getaddrinfo(host, 80, 0, socket.SOCK_STREAM))[0][-1])
							addr = (addr, ip, socket.inet_ntop(socket.AF_INET6,(list(filter(lambda x: x[0] == socket.AF_INET6, socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)))[0][-1])),port)
							self.output_method(0,addr[1]+", " + str(addr[2]))
						except IndexError:
							self.output_method(0,addr[1])
					socket_base = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					if verbose > 0:
						self.output_method(1,"Connecting to " + location + " (" + host + ")|" + str(addr[1]) + "|:" + str(addr[2]) + "... ")
					try:
						socket_connect = socket_base
						socket_connect.connect(socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)[0][-1])
						if verbose > 0:
							self.output_method(0,"connected.")
						ind = bytes("GET /" + path + " HTTP/1.0\r\nHost: " + host + "\r\n\r\n",'utf8')
						socket_connect.send(ind)
						if verbose > 0:
							self.output_method(1,"HTTP request sent, awaiting response... ")
							break
					except:
						if verbose > 0:
							self.output_method(0,"Unable to establish a connection to " + host)
						else:
							response.append("Unable to establish a connection to " + host)
						break
				if resolve_failure:
					if verbose <= 1:
						response.append(self.output_method(0,"failed"))
					continue
				local_file = False
				headers = True
				content_length = False
				content_type = False
				download_progress = 0
				download_progress_show = 0
				download_buffer_rate = 5
				download_buffer_size = self.buffer
				try:
					while True:
						data = socket_connect.recv(download_buffer_size)
						if headers:
							headers = False
							header_length = len(data)
							verification_position = 9
							try:
								data = data.decode()
								data = data.split("\r\n")
							except:
								if len(str(data).split("\\r\\n")) <= 1:
									pass
								else:
									verification_position = 11
									data = str(data).split("\\r\\n")
							if verbose > 0:
								self.output_method(0,data[0][verification_position:(verification_position+3)])
							if not data[0][verification_position:(verification_position+3)] in ["200","301","302"]:
								raise Exception("bad response")
							expect_new_location = False
							if data[0][verification_position:(verification_position+3)] in ["301","302"]:
								expect_new_location = True
							data_relay = False
							for header in data:
								if data_relay != False:
									if data_relay == True:
										data_relay = []
									data_relay.append(bytes(header,"utf-8"))
									continue
								if header == "":
									if data_relay == False:
										data_relay = True
								if verbose == 2:
									self.output_method(0,header)
								if header.startswith("Content-Length: "):
									content_length = int(header[16:]) + header_length
								elif header.startswith("Content-Type: "):
									content_type = header[14:].split(";")[0]
								elif header.startswith("Location: "):
									if expect_new_location == True:
										expect_new_location = header[10:]
							if expect_new_location != False:
								if expect_new_location == True:
									if verbose > 0:
										self.output_method(0,"Location: unknown")
									raise Exception("bad response")
								else:
									if verbose > 0:
										self.output_method(0,"Location: " + expect_new_location + " [following]")
									locations.insert(resource_iteration,expect_new_location)
									wget_download_iteration -= 1
									raise Exception("301 Moved Permanently")
							if data_relay != False:
								if data_relay == True:
									headers = True
									continue
							local_file = False
							if len(path) > 0:
								path = path.split("/")
								path = path[-1]
								path = path.split("?")
								path = path[0]
								filename = path
								if os.path.exists(filename):
									duplication_prevention = 1
									while os.path.exists(str(filename) + "." + str(duplication_prevention)):
										duplication_prevention += 1
									filename = filename + "." + str(duplication_prevention)
								local_file = open(filename, "wb")
							if content_type != False:
								if len(path) == 0:
									filename = False
									if content_type in default_file_mime_types.keys():
										filename = "index" + default_file_mime_types[content_type]
									else:
										filename = "download"
									path = filename
								elif content_type in list(default_file_mime_types.keys()):
									filename = path
									path = filename
								if os.path.exists(path):
									duplication_prevention = 1
									while os.path.exists(str(path) + "." + str(duplication_prevention)):
										duplication_prevention += 1
									path = path + "." + str(duplication_prevention)
								local_file = open(path,"wb")
							if content_length != False:
								try:
									if verbose == 1:
										self.output_method([0,1][content_type != False],"Length: " + str(content_length) + " (" + str(round(content_length / math.pow(download_buffer_size,int(math.floor(math.log(content_length, download_buffer_size)))), 2)) + ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")[int(math.floor(math.log(content_length, download_buffer_size)))] + ")")
										if content_type != False:
											self.output_method(0," [" + content_type + "]")
								except:
									pass
							if verbose > 0:
								self.output_method(0,"Saving to: '" + path + "'")
								if content_length != False:
									self.output_method(1,path + "    [")
								else:
									self.output_method(0,path + "    ~  downloading...")
							if data_relay != False:
								data = data_relay
							else:
								continue
						if local_file == False:
							if verbose > 0:
								response.append(self.output_method(0,"Unable to create a download location for the resource from '" + location + "'"))
							else:
								response.append("Unable to create a download location for the resource from '" + location + "'")
							raise Exception("download location failure")
						if len(data) <= 0:
							break
						download_progress += 1
						if verbose > 0:
							if content_length != False:
								download_percentage = (download_progress * download_buffer_size)*(100/content_length)
								if download_percentage > download_progress_show:
									while download_percentage >= download_progress_show:
										download_progress_show += download_buffer_rate
										self.output_method(1,"=")
						if type(data) == list:
							for data_sub in data:
								local_file.write(data_sub)
						else:
							local_file.write(data)
				except OSError:
					if content_length != "Unknown":
						download_rate_display_end = str(int(download_progress * download_buffer_size)) + "/" + str(content_length)
					else:
						download_rate_display_end = str(int(download_progress * download_buffer_size))
					if verbose > 0:
						if content_length != False:
							while download_progress_show < 100:
								download_progress_show += download_buffer_rate
								self.output_method(1," ")
								pass
						self.output_method(0, "] saved [" + str(download_rate_display_end) + "] - Connection timed out")
					else:
						response.append(location + " - Connection timed out")
					continue
				except Exception as e:
					e = str(e)
					if local_file != False:
						local_file.close()
					if e == "bad response":
						if verbose > 0:
							response.append(self.output_method(0,"'" + path  + "' failed to download"))
						else:
							response.append("'" + path + "' failed to download")
					elif e in ["download location failure","301 Moved Permanently"]:
						socket_connect.close()
						socket_base.close()
					if verbose > 0:
						self.output_method(0,"")
					continue
				except:
					if verbose > 0:
						if content_length != False:
							while download_progress_show < 100:
								download_progress_show += download_buffer_rate
								self.output_method(1," ")
								pass
				if content_length != False:
					if content_length < (download_progress * download_buffer_size):
						download_progress = content_length / download_buffer_size
					if verbose > 0:
						try:
							self.output_method(0,"] " + str(round(content_length / math.pow(download_buffer_size,int(math.floor(math.log((download_progress * download_buffer_size), download_buffer_size)))), 2)) + ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")[int(math.floor(math.log((download_progress * download_buffer_size), download_buffer_size)))])
						except:
							self.output_method(0,"]")
				if content_length == False:
					content_length = "Unknown"
				if download_progress > 0:
					if verbose > 0:
						if content_length != "Unknown":
							response.append(self.output_method(0,"'" + path + "' saved [" + str(int(download_progress * download_buffer_size)) + "/" + str(content_length) + "]"))
						else:
							response.append(self.output_method(0,"'" + path + "' saved [" + str(int(download_progress * download_buffer_size)) + "]"))
					else:
						response.append(self.pretty_time(format_string="%Y-%m-%d %H:%M:%S") + " URL:" + location + " [" + str(int(download_progress * download_buffer_size)) + "] -> '" + path + "' [" + str(wget_download_iteration) + "]")
				else:
					if verbose > 0:
						response.append(self.output_method(0,"'" + path  + "' failed to download"))
					else:
						response.append("'" + path + "' failed to download")
				socket_connect.close()
				socket_base.close()
				if verbose > 0:
					self.output_method(0,"")
		if verbose > 0:
			response = []
		return response

	def help(self,args=[]):
		response = ["MicroPython terminal, version " + " ".join(self.uname(["-v"])) + " (" + " ".join(self.uname(["-r"])) + ")",
				"These shell commands are defined internally. Type 'help' to see this list.",
				"Type 'man name' to find out more about the function 'name'.",
				"",
				"A star (*) next to a name means that the command is disabled.",
				""]
		for to_responsed in [{True:[command,self.man(["-f",command])],False:command}[self.man(["-f",command])!=[]] for command in sorted(self.get_all_command_bases().keys())]:
			if type(to_responsed) == list:
				to_responsed[1] = to_responsed[1][0].lower()
				response.append(" - ".join(to_responsed))
			else:
				response.append(to_responsed)
		return response
	def man(self,args=[]):
		response = []
		what_is = False
		command = None
		for arg in args:
			if arg.startswith("-"):
				if arg in ["-f","--what-is"]:
					what_is = True
				elif command == None:
					raise ValueError(arg)
			elif command == None:
				command = arg
		if command == None:
			return ["What manual page do you want?"]
		else:
			current_directory = self.get_display_cwd()
			self.change_directory(["/usr/share/man"])
			if command+".man" in self.ls(["-A","--color","never"]):
				command = self.concatenate([command+".man"])
				parsed = {}
				formatted_layout = []
				last_header = None
				for line in command:
					if line.count("	") == 0:
						if line != last_header:
							line = line.lstrip()
							parsed[line] = []
							formatted_layout.append(line)
							last_header = line
					else:
						parsed[last_header].append(line.lstrip())
				if what_is:
					if "ABOUT" in formatted_layout:
						response = parsed["ABOUT"]
				else:
					for heading in formatted_layout:
						parse = parsed[heading]
						response.append(heading)
						has_sub_children = False
						for contents in parse:
							if not contents.startswith("-"):
								contents = "   " + contents
								if has_sub_children:
									contents = "   " + contents
							else:
								contents = "   " + contents
								has_sub_children = True
							response.append(contents)
			self.change_directory([current_directory])
		return response

def terminal_parse(command = "", output = True, terminal = False):
	if terminal == False:
		return "Error: no terminal handler was provided"
	elif terminal.get_definition() != True:
		return "Error: terminal has not had a confirmed definition of objects"
	elif command.strip() == "":
		return ""
	else:
		commands = command.split("|")
		piped_commands = []
		alias = {}
		for alias_sub in terminal.alias(["-p"]):
			alias_sub = alias_sub[6:]
			alias_sub = alias_sub.split("='")
			alias_name = alias_sub.pop(0)
			alias[alias_name] = alias_name
			alias_sub = "='".join(alias_sub)
			alias_sub = alias_sub.split("'")
			alias[alias_name] = "'".join(alias_sub[0:-1])
		for command in commands:
			original_command = command
			command = parser_split(command,True,alias)
			command_bases = terminal.get_all_command_bases()
			if len(command) == 0:
				return "Error: syntax error no command occurred"
			if not command[0] in command_bases:
				return str(command[0]) + ": Command not found!"
			else:
				if command_bases[command[0]][3]:
					command = parser_split(original_command,False,{})
				piped_commands.append(command)
		del commands
		end_of_pipe = len(piped_commands)
		pipe_iteration = 0
		piped_command = None
		terminal.pipe_in = None
		ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
		for command in piped_commands:
			if command[0] in command_bases:
				if piped_command != None and command_bases[command[0]][2] == False:
					return "Error: unable to pipe into " + command[0]
				else:
					try:
						max_param_operations = 1
						for parameter in command[1:]:
							try:
								if not parameter[0] in [">","<"]:
									max_param_operations += 1
								else:
									break
							except:
								pass
						if len(command[1:]) == max_param_operations:
							max_param_operations = None
						if True:
							response = command_bases[command[0]][0](command[1:max_param_operations])
							command_data = command
							operator_values = []	
							get_next_output = False
							here_document = False
							output_type = False
							operation_to_file = []
							output_type_type_verification = -1
							for arg in command_data:
								if arg == ">":
									output_type = "wb"
									output_type_type_verification += 1
									operation_to_file.append([operator_values,[],"wb"])
									operator_values = []
									get_next_output = True
								elif arg == ">>":
									output_type = "ab"
									output_type_type_verification += 1
									operation_to_file.append([operator_values,[],"ab"])
									operator_values = []
									get_next_output = True
								elif get_next_output:
									if here_document:
										here_document = arg
									else:
										operation_to_file[output_type_type_verification][1].append(arg)
										operator_values.append(arg)
								elif arg == "<":
									pass
								elif arg == "<<":
									get_next_output = True
									here_document = True
							if here_document == True:
								return "Error: here document was requested but not defined"
							output_stat = False
							if output_type != False:
								for to_file in operation_to_file:
									if len(to_file) > 0:
										output_type = to_file[2]
										if type(response) != list:
											response = [response]
										for file in to_file[1]:
											rel_file = file
											file = self.dir_abspath(file)
											rel_file = file
											file = file.split("/")
											filename = False
											while filename == False:
												if len(file) == 0:
													return "Error: invalid location for here document"
												filename = file.pop()
												if len(filename) == "":
													filename = False
											file_raw_location = file
											file = "/".join([terminal.directory_restrict("/".join(file))[0],filename])
											try:
												existsing_lines = 0
												if output_type != "wb":
													if os.path.exists(file):
														existsing_lines = sum(1 for line in open(file,"rb"))
												with open(file,output_type) as output_file:
													if existsing_lines == 0:
														output_file.write(bytes(str("".join(ansi_escape.split(response.pop(0)))),"utf-8"))
													for input_to_output in response:
														output_file.write(bytes(str("\n" + "".join(ansi_escape.split(input_to_output))),"utf-8"))
													response = []
											except Exception as e:
												output_stat = True
												response = "Error: unable redirect output to be written to file '" + rel_file + "' as the encoding type is not dynamically supported"
									else:
										output_stat = True
										response = "Error: syntax error where output was expected"
							pipe_iteration += 1
							if pipe_iteration == end_of_pipe:
								if output_type == False:
									return_response = None
									if output == True:
										if command_bases[command[0]][1][0] == "null" and not output_stat:
											return_response = command_bases[command[0]][1][0] == None
										elif command_bases[command[0]][1][0] == "string" or output_stat:
											if response != None:
												return_response = str(response)
										elif command_bases[command[0]][1][0] == "join":
											if response != None:
												return_response = command_bases[command[0]][1][1].join(response)
										elif command_bases[command[0]][1][0] == "join/void":
											if response != None:
												return_response = command_bases[command[0]][1][1].join(response)
										elif command_bases[command[0]][1][0] == "string/void":
											if response != None:
												return_response = str(response)
										else:
											return_response = response
									else:
										return_response = response
									if return_response != None:
										if here_document != False:
											return_response += "\n" + here_document
										return return_response
							else:
								piped_command = command[0]
								if type(response) == list:
									for x in range(len(response)):
										response[x] = ansi_escape.sub("",response[x])
								terminal.pipe_in = response
					except ProcessLookupError as e:
						return "Fatal Error: missing reference for '" + str(e) + "'"
					except ReferenceError as e:
						return "Error: " + command[0] + " has a missing or invalid environment variable reference for '" + str(e) + "'"
					except ValueError as e:
						return "Error: invalid parameter '" + str(e) + "' in " + command[0]
			else:
				return "Command not found!"

class ProcessLookupError(Exception):
	pass

class ReferenceError(Exception):
	pass

class ValueError(Exception):
	pass

def randint(min, max):
	span = max - min + 1
	div = 0x3fffffff // span
	offset = random.getrandbits(30) // div
	val = min + offset
	return val

def parser_split(string,posix=True,alias={}):
	string = [char for char in string]
	position_of_occurence = []
	iteration_of_position = 0
	within_posix = False
	sibling_construct = None
	for char in string:
		if char in ["\"","\'"] and sibling_construct == None or char == sibling_construct:
			occurence_restructured = []
			completed_submask = False
			for submask in position_of_occurence:
				if len(submask) == 1:
					submask.append(iteration_of_position)
					completed_submask = True
				occurence_restructured.append(submask)
				if completed_submask:
					break
			within_posix = False
			sibling_construct = None
			if not completed_submask:
				within_posix = True
				sibling_construct = char
				occurence_restructured.append([iteration_of_position])
			position_of_occurence = occurence_restructured
		elif sibling_construct == None:
			position_of_occurence.append((char,within_posix))
		iteration_of_position += 1
	join_by = []
	temp_string = []
	for encapsulated in position_of_occurence:
		if len(encapsulated) == 1:
			encapsulated.append(-1)
		if encapsulated[1] == False:
			temp_string.append(encapsulated[0].replace("="," "))
		else:
			temp_string = "".join(temp_string).split()
			for temp_string_sub in temp_string:
				for alias_name, alias_value in alias.items():
					if temp_string_sub == alias_name:
						temp_string_sub = parser_split(alias_value)
				if type(temp_string_sub) != list:
					temp_string_sub = [temp_string_sub]
				join_by.extend(temp_string_sub)
			temp_string = []
			if encapsulated[1] < 0:
				continue
			if posix:
				encapsulated[0] += 1
				encapsulated[1] -= 1
			join_by.append("".join(string[encapsulated[0]:encapsulated[1] + 1]))
	if len(temp_string) > 0:
		temp_string = "".join(temp_string).split()
		for temp_string_sub in temp_string:
			for alias_name, alias_value in alias.items():
				if temp_string_sub == alias_name:
					temp_string_sub = parser_split(alias_value)
			if type(temp_string_sub) != list:
				temp_string_sub = [temp_string_sub]
			for temp_string_sub_increment in temp_string_sub:
				join_by.append(temp_string_sub_increment)
	return join_by


terminal = core()