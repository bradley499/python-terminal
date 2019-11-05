#!/usr/bin/env python3
# core.py

import os
import json
import shlex
import threading
import system

class core(threading.Thread):
	def __init__(self):
		self.set_all_command_bases()
		self.dir = False
		self.set_cwd(os.getcwd())
		self.process_id = None
		threading.Thread.__init__(self)

	def set_all_command_bases(self):
		self.command_bases = {"pwd":[self.get_cwd,["string"],False],"ls":[self.ls,["join"," "],False],"hostname":[self.get_hostname,["string"],False],"cd":[self.change_directory,["string/void"],False],"mkdir":[self.create_directory,["join/void","\n"],False],"rmdir":[self.remove_directory,["join/void","\n"],False],"cp":[self.copy,["join/void","\n"],False],"mv":[self.move,["join/void","\n"],False]}
		return True

	def get_all_command_bases(self):
		self.set_all_command_bases()
		return self.command_bases

	def set_proc(self,pid):
		self.process_id = pid

	def get_proc(self):
		return self.process_id

	def set_cwd(self,directory=False):
		if directory == False:
			return False
		else:
			self.dir = directory
			return self.dir;

	def get_cwd(self, args = []):
		if self.dir == "/":
			return "/"
		return self.dir

	def ls(self, args = []):
		files = [".",".."]
		reverse = False
		show_dirs = False
		show_hidden = False
		comma = False
		qoutation = False
		qouting_literal = False
		if len(args) >= 1:
			for arg in args:
				if arg == "-a":
					show_hidden = True
				elif arg == "-r":
					reverse = True
				elif arg == "-f":
					show_dirs = True
				elif arg == "-m":
					comma = True
				elif arg == "-q":
					qoutation = True
				elif arg == "-n":
					qouting_literal = True
				else:
					raise ValueError(arg)
		files = files + os.listdir(self.get_cwd())
		list_files = []
		for x in range(len(files)):
			if not show_hidden:
				if files[x][0] == ".":
					continue
			if not qoutation and not qouting_literal:
				if len(files[x].split(" ")) > 1:
					files[x] = "'" + files[x] + "'"
			if show_dirs and os.path.isdir(files[x]):
				files[x] = files[x] + "/"
			if qoutation:
				files[x] = "\"" + files[x] + "\""
			list_files.append(files[x])
			if comma and len(list_files) > 0:
				list_files[len(list_files) - 1] = list_files[len(list_files) - 1] + ","
		if reverse:
			list_files.reverse()
		return list_files

	def get_hostname(self):
		default = "user"
		try:
			with open("device.json","r") as device_details:
				try:
					device_details = json.loads(device_details.read())
					return device_details["name"]
				except:
					return default
		except:
			return default
		return default

	def move(self,args=[]):
		return self.copy(args,True)

	def copy(self,args=[],remove=False):
		verbose = False
		recursive = False
		copy_loc = []
		prepend_output = ""
		joint_command_type = "cp"
		if remove:
			prepend_output = "renamed "
			joint_command_type = "mv"
		if len(args) >= 1:
			for arg in args:
				if not arg.startswith("-"):
					copy_loc.append(arg)
				else:
					if arg == "-v":
						verbose = True
					elif arg == "-r":
						recursive = True
					else:
						raise ValueError(arg)
		else:
			return [joint_command_type + ": missing operand"]
		response = []
		if len(copy_loc) == 0:
			return [joint_command_type + ": missing operand"]
		elif len(copy_loc) < 2:
			return [joint_command_type + ": missing destination file operand after " . copy_loc[0]]
		current_base_dir = self.get_cwd()
		destination = copy_loc.pop()
		relative_destination = destination
		if not destination.startswith("/"):
			destination = os.path.abspath(current_base_dir + "/" + destination)
		for copy_default_loc in copy_loc:
			copy_default_loc_raw = copy_default_loc
			if copy_default_loc.startswith("/"):
				copy_default_loc = os.path.abspath(copy_default_loc)
			else:
				copy_default_loc = os.path.abspath(current_base_dir + "/" + copy_default_loc)
			copy_default_loc_absolute_base_delimiter = copy_default_loc.split("/")
			copy_default_loc_absolute_full_path = copy_default_loc_absolute_base_delimiter
			copy_default_loc_final_base_delimiter = copy_default_loc_absolute_base_delimiter[-1]
			copy_default_loc_absolute_base_delimiter = copy_default_loc_absolute_base_delimiter[:-1]
			copy_default_is_dir = True
			if copy_default_loc != "/":
				if self.change_directory([copy_default_loc]) == None:
					if recursive:
						self.change_directory([".."])
					else:
						response.append(joint_command_type + ": -r not specified so the directory '" + copy_default_loc + "' was omitted")
						continue
				elif self.change_directory(["/" + "/".join(copy_default_loc_absolute_base_delimiter)]) == None:
					copy_default_is_dir = False
					directory_contents = self.ls(["-a","-n"])
					if copy_default_loc_final_base_delimiter not in directory_contents:
						response.append(joint_command_type + ": cannot stat '" + copy_default_loc_raw + "' as no file or directory exists")
						continue
				else:
					response.append(joint_command_type + ": cannot stat '" + copy_default_loc_raw + "' as no file or directory exists")
					continue
			if copy_default_is_dir:
				destination_dir_directories = destination.split("/")
				directory_iteration = 0
				directory_child = True
				for directory in destination_dir_directories:
					if directory_iteration < len(copy_default_loc_absolute_full_path):
						if copy_default_loc_absolute_full_path[directory_iteration] == directory:
							if directory_child:
								directory_child = True
						else:
							directory_child = False
					directory_iteration += 1
				if directory_child:
					response.append(joint_command_type + ": cannot copy a directory '" + copy_default_loc_raw + "' into itself '" + destination + "'")
					continue
				else:
					files = [ 
						os.path.join(parent, name)
						for (parent, subdirs, files) in os.walk(copy_default_loc)
						for name in files + subdirs
					]
					files_directory_structure = []
					files_static_locations = []
					for file in files:
						if self.change_directory([file]) == None:
							files_directory_structure.append(file)
						else:
							files_static_locations.append(file)


					relative_delivery_destination = relative_destination
					self.change_directory([current_base_dir])
					if self.change_directory([destination]) != None:
						self.create_directory([destination,"-p"])
						if self.change_directory([destination]) != None:
							response.append(joint_command_type + ": unable to create the directory '" + relative_destination + "' to copy the contents of '" + copy_default_loc_raw + "'")
							continue
					else:
						delivery_destination = destination + "/" + copy_default_loc_final_base_delimiter
						relative_delivery_destination = relative_destination + "/" + copy_default_loc_final_base_delimiter
						if self.change_directory([destination]) != None:
							self.create_directory([destination,"-p"])
							if self.change_directory([destination]) != None:
								response.append(joint_command_type + ": unable to create the directory '" + relative_destination + "' to copy the contents of '" + copy_default_loc_raw + "' into")
								continue
					file_relational_tree = {}
					for file in files_static_locations:
						file = [file[len("/".join(copy_default_loc_absolute_full_path)) + 1:].split("/")]
						file.append(file[0].pop())
						file[0] = "/".join(file[0])
						if len(file[0]) == 0:
							file[0] = "."
						if not file[0] in list(file_relational_tree.keys()):
							file_relational_tree[file[0]] = []
						file_relational_tree[file[0]].append(file[1])
					del files_static_locations
					files_directory_structure.insert(0,".")
					for directory in files_directory_structure:
						self.change_directory([destination])
						if directory == ".":
							directory = ""
							if "." in list(file_relational_tree.keys()):
								for file in file_relational_tree["."]:
									if not os.path.isfile(self.get_cwd() + "/" + file) or remove:
										with open("/".join(copy_default_loc_absolute_full_path)+"/"+file,"rb") as file_contents:
											with open(self.get_cwd() + "/" + file, "wb") as file_save:
												file_save.write(file_contents.read())
												if verbose:
													response.append(prepend_output+"'" + "/".join(copy_default_loc_absolute_full_path)[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "/" + file + "' -> '" + relative_delivery_destination + "/" + file + "'")
										if remove:
											os.remove("/".join(copy_default_loc_absolute_full_path)+"/"+file)
									elif verbose:
										response.append("'" + "/".join(copy_default_loc_absolute_full_path)[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "/" + file + "' -> IGNORED")
							continue
						self.create_directory([directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:],"-p"])
						if self.change_directory([directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:]]) != None:
							response.append(joint_command_type + ": unable to copy the contents of the directory '" + directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:] + "'")
							continue
						else:
							response.append("'" + directory[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "' -> '" + relative_delivery_destination + "/" + directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:] + "'")
							for sub_directory, files in file_relational_tree.items():
								if sub_directory == directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:]:
									for file in files:
										if not os.path.isfile(self.get_cwd() + "/" + file) or remove:
											with open(directory+"/"+file,"rb") as file_contents:
												with open(self.get_cwd() + "/" + file, "wb") as file_save:
													file_save.write(file_contents.read())
													if verbose:
														response.append(prepend_output+"'" + directory[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "/" + file + "' -> '" + relative_delivery_destination + "/" + directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:] + "/" + file + "'")
											if remove:
												os.remove(directory+"/"+file,"rb")
										elif verbose:
											response.append("'" + directory[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "/" + file + "' -> IGNORED")
			elif not os.path.isfile(destination) or remove:
				with open("/".join(copy_default_loc_absolute_full_path),"rb") as file_contents:
					with open(destination,"wb") as file_save:
						file_save.write(file_contents.read())
						if verbose:
							response.append(prepend_output+"'" + copy_default_loc_raw + "' -> '" + relative_destination + "'")
				if remove:
					os.remove("/".join(copy_default_loc_absolute_full_path))
		self.change_directory([current_base_dir])
		return response



	def concatenate(self, args=[], outputLength = True):
		return False
		'''
		Not yet implemented
		if len(args) >= 1:
			for arg in args:
				if not arg.startswith("-"):
					dir_listings.append(arg)
				else:
					if arg == "":
						arg_type = True
					elif arg == "-p":
						arg_type_2 = True
					else:
						raise ValueError(arg)
		else:
			return ["mkdir: missing operand"]
		response = []
		if len(dir_listings) == 0:
			return ["mkdir: missing operand"]
	'''

	def change_directory(self, args=[]):
		if len(args) > 0:
			if len(args) == 1 and args[0] == "/":
				directory = "/"
			else:
				current_directory = self.get_cwd()
				if args[0].startswith("/"):
					directory = os.path.normpath(args[0])
					if directory != args[0]:
						return "cd: " + args[0] + "is not a valid directory path"
				else:
					if current_directory != "/":
						current_directory = current_directory + "/"
					directory = os.path.normpath(current_directory + args[0])
			if os.path.isdir(directory):
				self.set_cwd(directory)
			else:
				return "cd: " + args[0] + " is not a directory"

	def create_directory(self, args=[]):
		verbose = False
		create_directory_parents = False
		dir_listings = []
		if len(args) >= 1:
			for arg in args:
				if not arg.startswith("-"):
					dir_listings.append(arg)
				else:
					if arg == "-v":
						verbose = True
					elif arg == "-p":
						create_directory_parents = True
					else:
						raise ValueError(arg)
		else:
			return ["mkdir: missing operand"]
		current_base_dir = self.get_cwd().split("/")[1:]
		response = []
		if len(dir_listings) == 0:
			return ["mkdir: missing operand"]
		for dir_new in dir_listings:
			dir_new_default_string = dir_new
			if dir_new_default_string[0] == "/":
				dir_new_default_string = dir_new_default_string.split("/")[1:]
			else:
				dir_new_default_string = os.path.abspath("/" + "/".join(current_base_dir) + "/" + dir_new_default_string).split("/")[1:]
			dir_string = ""
			dir_deviate_sub_name = ""
			dir_deviate_destination_name = ""
			dir_child_iteration = 0
			small_relative_dir_creation = [""]
			for dir_new_sub_name in dir_new_default_string:
				dir_base_use = False
				dir_new_sub_name_generation_continue = True
				if dir_child_iteration < len(current_base_dir):
					dir_base_use = True
				if dir_base_use:
					if dir_new_sub_name == current_base_dir[dir_child_iteration]:
						dir_string = dir_string + "/" + dir_new_sub_name
						dir_new_sub_name_generation_continue = False
				if dir_new_sub_name_generation_continue:
					if dir_child_iteration == len(dir_new_default_string) - 1:
						dir_deviate_destination_name = dir_new_sub_name
						if len(small_relative_dir_creation) > 1:
							small_relative_dir_creation.append(small_relative_dir_creation[-1] + "/" + dir_new_sub_name)
						else:
							small_relative_dir_creation.append(small_relative_dir_creation[-1] + dir_new_sub_name)
					else:
						dir_deviate_sub_name = dir_deviate_sub_name + "/" + dir_new_sub_name
						if len(small_relative_dir_creation) > 1:
							small_relative_dir_creation.append(small_relative_dir_creation[-1] + "/" + dir_new_sub_name)
						else:
							small_relative_dir_creation.append(small_relative_dir_creation[-1] + dir_new_sub_name)
				dir_child_iteration += 1
			dir_child_iteration = 1
			if self.change_directory([dir_string]) == None:
				if len(dir_deviate_sub_name) == 0:
					if self.change_directory([self.get_cwd() + "/" + dir_deviate_destination_name]) != None:
						os.mkdir(self.get_cwd() + "/" + dir_deviate_destination_name)
						if verbose:
							response.append("mkdir: created directory '" + dir_deviate_destination_name + "'")
					else:
						response.append("mkdir: cannot create directory '" + dir_deviate_destination_name + "' as directory exists")
				else:
					dir_active_recent = "."
					dir_creation_failed = False
					dir_new_sub_name_iteration = 0
					for dir_new_sub_name in dir_deviate_sub_name.split("/")[1:]:
						dir_new_sub_name_iteration += 1
						if self.change_directory([dir_new_sub_name]) != None:
							if create_directory_parents:
								os.mkdir(self.get_cwd() + "/" + dir_new_sub_name)
								self.change_directory([dir_new_sub_name])
								dir_string = dir_string + "/" + dir_new_sub_name
								if verbose:
									response.append("mkdir: created directory '" +  small_relative_dir_creation[dir_child_iteration] + "'")
							else:
								while dir_child_iteration < len(small_relative_dir_creation):
									response.append("mkdir: cannot create directory '" + small_relative_dir_creation[dir_child_iteration] + "' as no file or directory exists")
									dir_child_iteration += 1
									dir_creation_failed = True
								break
						if dir_new_sub_name_iteration == (len(dir_deviate_sub_name.split("/")) - 1):
							self.change_directory([".."])
						dir_child_iteration+=1
						dir_active_recent = dir_new_sub_name
					if not dir_creation_failed:
						if self.change_directory([dir_active_recent]) == None:
							if self.change_directory([dir_deviate_destination_name]) != None:
								os.mkdir(self.get_cwd() + "/" + dir_deviate_destination_name);
								if verbose:
									response.append("mkdir: created directory '" +  small_relative_dir_creation[-1] + "'")
							else:
								response.append("mkdir: cannot create directory '" + small_relative_dir_creation[-1] + "' as directory exists")
						else:
							response.append("mkdir: cannot create directory '" + small_relative_dir_creation[-1] + "' as directory parent has vanish")
			else:
				response.append("mkdir: cannot create directory '" + dir_new_sub_name + "' as directory exists")
		current_base_dir = "/" + "/".join(current_base_dir)
		if self.get_cwd() != current_base_dir:
			self.change_directory([current_base_dir])
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
						dir_listings.append(self.get_cwd() + "/" + arg)
				else:
					if arg == "-v":
						verbose = True
					elif arg == "-p":
						delete_directory_parent = True
					else:
						raise ValueError(arg)
		else:
			return ["rmdir: missing operand"]
		if len(dir_listings) == 0:
			return ["rmdir: missing operand"]
		response = []
		current_base_dir = self.get_cwd().split("/")[1:]
		for dir_del in dir_listings:
			dir_delete_default_string = dir_del
			dir_del_default_string = os.path.abspath(dir_delete_default_string).split("/")[1:]
			if current_base_dir == dir_del_default_string:
				response.append("rmdir: failed to remove '" + self.get_cwd().split("/")[-1] + "' as the current directory cannot be deleted")
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
					directory_contents = self.ls(["-a"])
					if directory_contents != [".",".."]:
						response.append("rmdir: failed to remove '/" + small_relative_dir_creation[dir_deletion_iteration] + "' as directory is not empty")
					else:
						self.change_directory([".."])
						if verbose:
							response.append("rmdir: removing directory '" + small_relative_dir_creation[dir_deletion_iteration] + "'")
						os.rmdir(self.get_cwd() + "/" + dir_del_parent)
					dir_deletion_iteration+=1
					if self.get_cwd() == os.path.abspath(dir_string):
						break;
					elif not delete_directory_parent:
						break;
			else:
				if dir_del == "":
					dir_del = "/"
				else:
					dir_del = "/".join(small_relative_dir_creation)
				response.append("rmdir: failed to remove '" + dir_del + "' as no file or directory exists")
		current_base_dir = "/" + "/".join(current_base_dir)
		if self.get_cwd() != current_base_dir:
			self.change_directory([current_base_dir])
		return response

def terminal_parse(command = "", output = True, terminal = False):
	if terminal == False:
		return "Error: no terminal handler was provided"
	if command.strip() == "":
		return ""
	else: 
		command = shlex.split(command.strip(" "))
		command_bases = terminal.get_all_command_bases()
		if command[0] in command_bases:
			try:
				new_process = system.proc.new(" ".join(command),output)
				if new_process[0]:
					terminal.set_proc(new_process[1])
					pid = terminal.get_proc()
				else:
					return new_process[1]
				if command_bases[command[0]][2]:
					threading.Thread(target=self.command_bases[command[0]][0](command[1:]))
					return None
				else:
					response = command_bases[command[0]][0](command[1:])
					if output == True:
						if command_bases[command[0]][1][0] == "null":
							return command_bases[command[0]][1][0] == None
						if command_bases[command[0]][1][0] == "string":
							return str(response)
						elif command_bases[command[0]][1][0] == "join":
							if response != None:
								return command_bases[command[0]][1][1].join(response)
						elif command_bases[command[0]][1][0] == "join/void":
							if response != None:
								return command_bases[command[0]][1][1].join(response)
						elif command_bases[command[0]][1][0] == "string/void":
							if response != None:
								return str(response)
						else:
							return response
					else:
						return response
			except ValueError as e:
				return "Error: invalid parameter '" + str(e) + "'"
		else:
			return "Command not found!"




terminal = core()