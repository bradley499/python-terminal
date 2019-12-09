#!/usr/bin/env python3
# core.py

import os
import json
import shlex
import threading
import system
import urllib
import time

class core(threading.Thread):
	def __init__(self):
		self.set_all_command_bases()
		self.dir = False
		self.pipe_in = None
		self.set_cwd(os.getcwd())
		self.process_id = None
		self.input_method_reference = [[None,False],[None,False]]
		self.output_method_reference = [[None,False],[None,False]]
		self.definition_complete = False
		threading.Thread.__init__(self)

	def set_all_command_bases(self, args=[]):
		self.command_bases = {"pwd":[self.get_cwd,["string"],False,False,False],"ls":[self.ls,["join"," "],False,False,False],"hostname":[self.get_hostname,["string"],False,False,False],"cd":[self.change_directory,["string/void"],False,False,False],"mkdir":[self.create_directory,["join/void","\n"],False,False,False],"rmdir":[self.remove_directory,["join/void","\n"],False,False,False],"cat":[self.concatenate,["join","\n"],False,False,False],"head":[self.head,["join","\n"],False,False,False],"tail":[self.tail,["join","\n"],False,False,False],"cp":[self.copy,["join/void","\n"],False,False,False],"mv":[self.move,["join/void","\n"],False,False,False],"link":[self.link,["string"],False,False,False],"unlink":[self.unlink,["string"],False,False,False],"rm":[self.remove,["join/void","\n"],False,False,False],"exit":[self.exit,["null"],False,False,False],"clear":[self.clear,["null"],False,False,False],"grep":[self.grep,["join/void","\n"],False,True,True],"uniq":[self.uniq,["join/void","\n"],False,True,True]}
		return True

	def get_all_command_bases(self, args=[]):
		self.set_all_command_bases()
		return self.command_bases

	def set_definition(self,complete = False):
		self.definition_complete = complete
		system.proc.set_output_method(self.output_method_reference[0][0])

	def get_definition(self):
		return self.definition_complete

	def set_input_method(self,inputting_method = False, mode = -1):
		if inputting_method != False and mode != -1:
			if mode == 0:
				if callable(inputting_method):
					self.input_method_reference[0] = [inputting_method, True]
					return self.input_method_reference[0];
				else:
					return [ImportWarning("failed attempt to implement a non callable inputting method"),False]
			elif mode == 1:
				if callable(inputting_method):
					self.input_method_reference[1] = [inputting_method, True]
					return self.input_method_reference[1];
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
					return self.input_method_reference[0][0]() or " "
				else:
					raise NotImplementedError("no input mehod defined")
			elif mode == 1: # response value input
				if self.input_method_reference[1][1]:
					if not additions == False:
						self.output_method(1,additions)
					return self.input_method_reference[1][0]() or " "
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

	def set_proc(self,pid):
		self.process_id = pid

	def get_proc(self):
		return self.process_id

	def set_cwd(self,directory=False):
		if directory == False:
			return False
		else:
			self.dir = directory
			os.chdir(self.dir)
			return self.dir;

	def get_cwd(self,args=[]):
		if self.dir == "/":
			return "/"
		return self.dir

	def ls(self,args=[]):
		files = [".",".."]
		reverse = False
		show_dirs = False
		show_all = False
		comma = False
		qoutation = False
		qouting_literal = False
		if len(args) >= 1:
			for arg in args:
				if arg == "-a":
					show_all = True
				elif arg == "-A":
					files = []
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
			if not show_all:
				if files[x][0] == ".":
					continue
			if not qoutation and not qouting_literal:
				if len(files[x].split(" ")) > 1:
					files[x] = "'" + files[x] + "'"
			if show_dirs and os.path.isdir(os.path.abspath(self.get_cwd()+"/"+files[x])):
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
					if arg in ["-v","--verbose"]:
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
			return [joint_command_type + ": missing destination file operand after " + copy_loc[0]]
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
					elif not os.access(self.get_cwd() + "/" + copy_default_loc_final_base_delimiter, os.R_OK):
						response.append(joint_command_type + ": cannot stat '" + copy_default_loc_raw + "' as permission is denied")
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
										self.concatenate(["/".join(copy_default_loc_absolute_full_path)+"/"+file,">",self.get_cwd()+"/"+file])
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
							if verbose:
								response.append("'" + directory[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "' -> '" + relative_delivery_destination + "/" + directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:] + "'")
							for sub_directory, files in file_relational_tree.items():
								if sub_directory == directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:]:
									for file in files:
										if not os.path.isfile(self.get_cwd() + "/" + file) or remove:
											self.concatenate([directory+"/"+file,">",self.get_cwd() + "/" + file])
											if verbose:
												response.append(prepend_output+"'" + directory[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "/" + file + "' -> '" + relative_delivery_destination + "/" + directory[len("/".join(copy_default_loc_absolute_full_path)) + 1:] + "/" + file + "'")
											if remove:
												os.remove(directory+"/"+file,"rb")
										elif verbose:
											response.append("'" + directory[len("/".join(copy_default_loc_absolute_full_path)) - len(copy_default_loc_final_base_delimiter):] + "/" + file + "' -> IGNORED")
			elif not os.path.isfile(destination) or remove:
				self.concatenate(["/".join(copy_default_loc_absolute_full_path),">",destination])
				if verbose:
					response.append(prepend_output+"'" + copy_default_loc_raw + "' -> '" + relative_destination + "'")
				if remove:
					os.remove("/".join(copy_default_loc_absolute_full_path))
		self.change_directory([current_base_dir])
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
					if arg == "-n":
						line_count = True
					elif arg == "-e":
						end_of_line = True
					elif arg == "-t":
						show_tabulations = True
					elif arg == "-s":
						squeeze_blanks = True
					else:
						raise ValueError(arg)
				elif arg == ">":
					output_type = "wb"
					output_type_type_verification += 1
					operation_to_file.append([cat_values,[],"wb"])
					cat_values = []
					get_next_output = True
				elif arg == ">>":
					output_type = "ab"
					output_type_type_verification += 1
					operation_to_file.append([cat_values,[],"ab"])
					cat_values = []
					get_next_output = True
				elif get_next_output:
					operation_to_file[output_type_type_verification][1].append(arg)
					cat_values.append(arg)
				elif arg == "<":
					pass
				else:
					cat_values.append(arg)
			if get_next_output:
				if len(operation_to_file[-1][1]) == 0:
					return ["cat: syntax error where output was expected"]
		response = []
		output_error_stream = []
		if output_type != False:
			for to_file in operation_to_file:
				if len(to_file) > 0:
					output_type = to_file[2]
					input_stream = []
					if to_file[0] == []:
						while True:
							try:
								input_stream_buffer = self.input_method(0)
							except EOFError:
								break
							if line_count:
								input_stream.append(input_stream_buffer + "\n")
							else:
								input_stream.append(bytes(input_stream_buffer + "\n","utf-8"))
					else:
						files = []
						for file in to_file[0]:
							file_relative = file
							if not file.startswith("/"):
								file = self.get_cwd() + "/" + file
							file = os.path.abspath(file)
							if os.path.isfile(file):
								files.append([file,file_relative])
							else:
								response.append("cat: unable to use file '" + file_relative + "' for input stream as it does not exists")
						if len(response) > 0:
							return response
						else:
							for file in files:
								try:
									with open(file[0],"rb") as file:
										for file_lines in file.readlines():
											input_stream.append(file_lines)
								except Exception as e:
									output_error_stream.append("cat: unable to read the file '" + file_raw_location[1] + "' as the encoding type is not dynamically supported")
					previous_line = b''
					for file in to_file[1]:
						file_raw_location = file
						if not file.startswith("/"):
							file = self.get_cwd() + "/" + file
						file = os.path.abspath(file)
						try:
							with open(file,output_type) as output_file:
								total_lines_character_size = len(str(len(input_stream)))
								line_num = 0
								for input_to_output in input_stream:
									if show_tabulations:
										input_to_output = bytes(input_to_output.decode("utf-8").replace("\t","^I"),"utf-8")
									if end_of_line:

										input_to_output = input_to_output.decode("utf-8").splitlines(True)
										input_to_output[-1] = input_to_output[-1].splitlines(True)
										default_input_to_output = input_to_output[-1][-1]
										for escaped_character in ["\r\n","\r","\n"]:
											input_to_output[-1][-1] = input_to_output[-1][-1].replace(escaped_character,"$"+escaped_character,1)
											if default_input_to_output != input_to_output[-1][-1]:
												break
										if default_input_to_output == input_to_output[-1][-1]:
											input_to_output[-1].append("$")
										input_to_output[-1] = "".join(input_to_output[-1])
										input_to_output = "".join(input_to_output)
										input_to_output = bytes(input_to_output,"utf-8")
									if not (squeeze_blanks and previous_line == input_to_output and len(input_stream) > 0 and len(input_to_output) >= 0):
										if squeeze_blanks:
											previous_line = input_to_output
										if line_count:
											output_file.write(b"".join([bytes(str(((total_lines_character_size - len(str(line_num + 1)) + 1) * " ") + str(line_num + 1) + " "),"utf-8"),input_to_output]))
										else:
											output_file.write(input_to_output)
										line_num += 1
						except Exception as e:
							output_error_stream.append("cat: unable to write to file '" + file_raw_location + "' as the encoding type is not dynamically supported")
				else:
					response.append("cat: syntax error where output was expected")
		else:
			if len(cat_values) > 0:
				output_stream = []
				previous_line = None
				for file in cat_values:
					file_relative = file
					if not file.startswith("/"):
						file = self.get_cwd() + "/" + file
					file = os.path.abspath(file)
					if not os.path.isfile(file):
						output_error_stream.append("cat: unable to use file '" + file_relative + "' for input stream as it does not exists")
					else:
						try:
							with open(file,"rb") as output_file:
								for line in output_file.readlines():
									line = line.decode("utf-8")
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
		get_next_paramter = [False,False]
		response = []
		files = []
		joint_command_type = "head"
		if reverse:
			joint_command_type = "tail"
		for arg in args:
			if get_next_paramter[0]:
				if get_next_paramter[1] == "-n":
					if arg.isdigit():
						arg = int(arg)
						if arg > 0:
							total_lines = arg
							continue
				response.append(joint_command_type + ": invalid number of lines '" + arg + "'")
				continue
			if arg.startswith("-"):
				if arg == "-n":
					get_next_paramter = [True,arg]
				else:
					raise ValueError(arg)
			else:
				files.append(arg)
		file_iteration = 0
		for file in files:
			file_raw_location = file
			if not file.startswith("/"):
				file = self.get_cwd() + "/" + file
			file = os.path.abspath(file)
			if not os.path.isfile(file):
				if os.path.isdir(file):
					response.append(joint_command_type + ": unable to read '" + file_raw_location + "' as it is a directory")
				else:
					response.append(joint_command_type + ": unable to read '" + file_raw_location + "' as no file or directory exists")
			else:
				file_contents = self.concatenate([file])
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
					if arg in ["-v","--verbose"]:
						verbose = True
					elif arg in ["-p","--parents"]:
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

	def link(self, files=[]):
		if len(files) > 1:
			if len(files) == 1:
				return "link: missing operand after '" + files[0] + "'"
			elif len(files) == 2:
				files_raw = files
				if not files[0].startswith("/"):
					files[0] = os.path.abspath(files[0])
				if os.path.exists(files[0]):
					if os.path.isfile(files[0]):
						if not files[1].startswith("/"):
							files[1] = os.path.abspath(files[1])
						if os.path.exists(files[1]):
							return "link: cannot create link from '" + files_raw[0] + "' as the file '" + files_raw[1] + "' exists"
						else:
							os.link(files[0],files[1])
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
			if not file.startswith("/"):
				file = os.path.abspath(file)
			if os.path.exists(file):
				if os.path.isfile(file):
					os.unlink(file)
					return None
				else:
					return "unlink: cannot unlink '" + file + "' as it is a directory"
			else:
				return "unlink: cannot unlink '" + file + "' as no file or directory"

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
					if arg in ["-v","verbose"]:
						verbose = True
					elif arg in ["-f","--force"]:
						force = True
						prompt_every = False
						prompt_3_plus = False
					elif arg  == "-i" and not force:
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
			for remove in to_remove:
				file_raw_location = remove
				if not remove.startswith("/"):
					remove = os.path.abspath(remove)
				if remove.endswith("*"):
					remove = remove.split("/")
					if remove[-1] == "*":
						remove.pop()
					if remove == [""]:
						remove = "/"
					else:
						remove = "/".join(remove)
				if os.path.exists(remove):
					if os.path.isdir(remove):
						to_remove_tree_rel = []
						if recursive:
							to_remove_tree_rel.extend([ 
								[os.path.abspath(os.path.join(parent, name)),os.path.isdir(os.path.join(parent, name))]
								for (parent, subdirs, files) in os.walk(remove)
								for name in files + subdirs
							])
						else:
							to_remove_files_rel = [[os.path.abspath(file),file[-1] == "/"] for file in self.ls(["-A","-f"])]
							to_remove_tree_rel.extend(to_remove_files_rel)
						for to_remove_tree_loc in to_remove_tree_rel:
							is_relative = False
							is_dir = False
							if len(to_remove_tree_loc) == 2:
								is_dir = to_remove_tree_loc[1]
							elif to_remove_tree_loc[0][-1] == "/":
								is_dir = True
							if to_remove_tree_loc[0].startswith(self.get_cwd()):
								is_relative = True
								to_remove_tree_loc[0] = to_remove_tree_loc[0][len(self.get_cwd())+1:]
							to_remove_tree_loc[0] = to_remove_tree_loc[0].split("/")
							if to_remove_tree_loc[0][-1] == "":
								del to_remove_tree_loc[0][-1]
							if to_remove_tree_loc[0][0] == "" and not is_relative:
								del to_remove_tree_loc[0][0]
							if to_remove_tree_loc[-1] == "":
								to_remove_tree.append([to_remove_tree_loc[0].pop(),to_remove_tree_loc[0],is_relative,True,is_dir])
							if len(to_remove_tree_loc) > 1:
								to_remove_tree.append([to_remove_tree_loc[0].pop(),to_remove_tree_loc[0],is_relative,False,is_dir])
							else:
								to_remove_tree.append([to_remove_tree_loc[0],None,False,False,is_dir])
					elif os.path.isfile(remove):
						to_remove_tree.append([remove,None,False,True,False])
				else:
					response.append("rm: cannot remove '" + file_raw_location + "' as no file or directory exists")
			if len(to_remove_tree) > 0:
				to_remove_tree_sorted = []
				to_remove_tree_sorted_none = []
				for file in to_remove_tree:
					if file[1] == None:
						file[1] = []
						to_remove_tree_sorted_none.append(file)
					else:
						to_remove_tree_sorted.append(file)
				sorted(to_remove_tree_sorted,key=lambda x: x[1], reverse=True)
				to_remove_tree_sorted_none.extend(to_remove_tree_sorted)
				to_remove_tree = to_remove_tree_sorted_none
				del to_remove_tree_sorted
				del to_remove_tree_sorted_none
				if (prompt_3_plus and len(to_remove_tree) > 3) or recursive:
					if recursive:
						if not prompt_every:
							if self.input_method(1,"rm: remove " + str(len(to_remove_tree)) + " arguments recursively? ")[0] != "y":
								return None
					elif self.input_method(1,"rm: remove " + str(len(to_remove_tree)) + " arguments? ")[0] != "y":
						return None
				current_base_dir = self.get_cwd()
				current_directory = []
				to_remove_tree_build = {None:[]}
				for file in to_remove_tree:
					if file[4]:
						del file[4]
						if file[1] == []:
							to_remove_tree_build[file[0]] = []
						else:
							to_remove_tree_build["/".join(file[1] + [file[0]])] = []
					elif file[1] == []:
						del file[4]
						to_remove_tree_build[None].append(file)
					else:
						del file[4]
						to_remove_tree_build["/".join(file[1])].append(file)
				to_remove_tree = {None:to_remove_tree_build[None]}
				to_remove_tree_build.pop(None)
				directory_name_keys = [*to_remove_tree_build.keys()]
				directory_name_keys.sort()
				directory_name_keys_iteration = []
				for directory in directory_name_keys:
					directory_layout = [directory]
					for sub_directory in to_remove_tree_build:
						if sub_directory != directory:
							if sub_directory.startswith(directory+"/"):
								directory_layout.append(sub_directory)
					directory_layout = sorted(directory_layout)
					for directory in directory_layout:
						directory_name_keys_iteration.append(directory)
					directory_layout = sorted(directory_layout,key=lambda x: os.path.splitext(x))
					for directory in directory_layout:
						to_remove_tree[directory] = to_remove_tree_build[directory]
				to_remove_directories = []
				for directory_name, files in to_remove_tree.items():
					if directory_name != None:
						directory_name = directory_name.split("/")
					else:
						directory_name = []
					if directory_name != [] and files == []:
						has_children = False
						for directory in to_remove_tree.keys():
							if directory == None:
								continue
							if directory.startswith("/".join(directory_name)+"/"):
								has_children = True
								break
						if not has_children:
							if not recursive:
								response.append("rm: cannot remove '" + "/".join(directory_name) + "' as it is a directory")
							elif prompt_every:
								if self.input_method(1,"rm: remove directory '" + "/".join(directory_name) + "'? ")[0] == "y":
									if self.remove_directory(["/".join(directory_name)]) != []:
										response.append("rm: cannot remove directory '" + "/".join(directory_name) + "'")
									elif verbose:
										response.append("removed '" + "/".join(directory_name) + "'")
							elif self.remove_directory(["/".join(directory_name)]) != []:
								response.append("rm: cannot remove directory '" + "/".join(directory_name) + "'")
							elif verbose:
								response.append("removed '" + "/".join(directory_name) + "'")
						else:
							if prompt_every:
								if self.input_method(1,"rm: descend into directory '" + "/".join(directory_name) + "'? ")[0] != "y":
									directory_name_keys_iteration_sub = directory_name_keys_iteration
									for directory in directory_name_keys_iteration_sub:
										if directory.startswith("/".join(directory_name)+"/"):
											directory_name_keys_iteration.remove(directory)
											to_remove_directories.remove(directory)
									continue
							to_remove_directories.insert(0,directory_name)
					else:
						if directory_name != []:
							is_a_child = 0
							if len(to_remove_directories) > 0:
								if current_directory == to_remove_directories[0]:
									to_remove_directories.reverse()
									for dir_remove in to_remove_directories:
										has_children = False
										for directory in to_remove_directories:
											if directory == None:
												continue
											if "/".join(directory).startswith("/".join(directory_name)+"/"):
												has_children = True
												break
										if not has_children and dir_remove in directory_name_keys_iteration:
											if dir_remove[:len(current_directory)] != current_directory:
												if not recursive:
													response.append("rm: cannot remove '" + "/".join(current_directory) + "' as it is a directory")
												elif prompt_every:
													if self.input_method(1,"rm: remove directory '" + "/".join(directory_name) + "'? ")[0] == "y":
														if self.remove_directory(["/".join(directory_name)]) != []:
															response.append("rm: cannot remove directory '" + "/".join(directory_name) + "'")
														elif verbose:
															response.append("removed '" + "/".join(directory_name) + "'")
												elif self.remove_directory(["/".join(directory_name)]) != []:
													response.append("rm: cannot remove directory '" + "/".join(directory_name) + "'")
												elif verbose:
													response.append("removed '" + "/".join(file[1])+"/"+file[0] + "'")
												to_remove_directories.remove(directory_name)
									to_remove_directories.reverse()
							if prompt_every:
								if self.input_method(1,"rm: descend into directory '" + "/".join(directory_name) + "'? ")[0] != "y":
									directory_name_keys_iteration_sub = directory_name_keys_iteration
									for directory in directory_name_keys_iteration_sub:
										if directory.startswith("/".join(directory_name)+"/"):
											directory_name_keys_iteration.remove(directory)
											to_remove_directories.remove(directory)
									continue
							to_remove_directories.insert(0,directory_name)
						current_directory = directory_name
						for file in files:
							if file != [None,[],False,False]:
								file_name_raw_concatenated = file[0]
								if file[3]:
									file_name_raw_concatenated = file[0]
								else:
									if file[1] != None and file[1] != []:
										file_name_raw_concatenated = "/".join(directory_name) + "/" + file[0]
									if not file[2]:
										file_name_raw_concatenated = current_base_dir + "/" + "/".join(directory_name) + "/" + file[0]
								if prompt_every:
									if len(self.concatenate([file_name_raw_concatenated])) == 0:
										if self.input_method(1,"rm: remove regular empty file '" + file_name_raw_concatenated + "'? ")[0] != "y":
											continue
									elif self.input_method(1,"rm: remove regular file '" + file_name_raw_concatenated + "'? ")[0] != "y":
										continue
								if self.unlink([file_name_raw_concatenated]) != None:
									if system.proc.is_fg_type(self.process_id):
										self.output_method(0,"rm: cannot remove '" + file_name_raw_concatenated + "'")
									else:
										response.append("rm: cannot remove '" + file_name_raw_concatenated + "'")
								elif verbose:
									if system.proc.is_fg_type(self.process_id):
										self.output_method(0,"removed '" + file_name_raw_concatenated + "'")
									else:
										response.append("removed '" + file_name_raw_concatenated + "'")
				if current_directory != []:
					to_remove_directories = sorted(to_remove_directories,key=lambda x: os.path.splitext("/".join(x)))
					while len(to_remove_directories) > 0:
						for dir_remove in to_remove_directories:
							dir_remove = "/".join(dir_remove)
							if not recursive:
								response.append("rm: cannot remove '" + dir_remove + "' as it is a directory")
								to_remove_directories.remove(dir_remove)
							else:
								has_children = False
								for directory in to_remove_directories:
									if directory == None:
										continue
									if "/".join(directory).startswith(dir_remove+"/"):
										has_children = True
										break
								if not has_children:
									if prompt_every:
										if self.input_method(1,"rm: remove directory '" + dir_remove + "'? ")[0] == "y":
											if self.remove_directory([dir_remove]) != []:
												response.append("rm: cannot remove directory '" + dir_remove + "'")
											elif verbose:
												response.append("removed '" + dir_remove + "'")
									elif self.remove_directory([dir_remove]) != []:
										response.append("rm: cannot remove directory '" + dir_remove + "'")
									elif verbose:
										response.append("removed '" + dir_remove + "'")
									to_remove_directories.remove(dir_remove.split("/"))
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
					if arg in ["-v","--verbose"]:
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
			if dir_del.startswith("/"):
				is_root = "/"
			else:
				is_root = ""
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
						response.append("rmdir: failed to remove '" + is_root + small_relative_dir_creation[dir_deletion_iteration] + "' as directory is not empty")
					else:
						self.change_directory([".."])
						if verbose:
							response.append("rmdir: removing directory '" + is_root + small_relative_dir_creation[dir_deletion_iteration] + "'")
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

	def grep(self,args=[]):
		if self.pipe_in == None:
			return ["grep: missing piped input stream"]
		else:
			response = []
			response_raw = []
			line_count = False
			ignore_case = False
			quiet = False
			max_lines = -1
			search = None
			get_next_paramter = [False,False]
			for arg in args:
				if get_next_paramter[0]:
					if get_next_paramter[1] == "-m":
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
					elif arg == "-i":
						ignore_case = True
					elif arg == "-m":
						get_next_paramter = [True,"-m"]
					elif arg in ["-q","--quiet","--silent"]:
						quiet = True
					else:
						raise ValueError(arg)
				elif shlex.split(arg) != arg:
					search = " ".join(shlex.split(arg))
					continue
			if search == None:
				return ["grep: missing search parameter"]
			if ignore_case:
				search = search.lower()
			if type(self.pipe_in) != list:
				if type(self.pipe_in) == str:
					self.pipe_in = self.pipe_in.split(" ")
			entry_line_number = 0
			for entry in self.pipe_in:
				actual_entry = entry
				if ignore_case:
					entry = entry.lower()
				entry_line_number += 1
				if entry.find(search) >= 0:
					if quiet:
						return None
					response_raw.append((entry_line_number,actual_entry))
					if max_lines >= 0:
						if len(response_raw) >= max_lines:
							break
			total_lines_character_size = len(response_raw)
			for entry in response_raw:
				if line_count:
					response.append(str(entry[0]) + ":" + entry[1])
				else:
					response.append(entry[1])
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
					elif arg in ["-i","--ignore_case"]:
						ignore_case = True
					elif arg in ["-u","--unique"]:
						only_unique = True
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

	def exit(self,args=[]):
		raise SystemExit("exit")
		return None

	def clear(self,args=[]):
		raise SystemExit("clear")
		return None

	def ping(self,args=[]):
		'''
		Not implemented yet
		'''
		return False

	def wget(self,args=[]):
		'''
		Not implemented yet
		'''
		return False

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
		for command in commands:
			original_command = command
			command = shlex.split(command)
			command_bases = terminal.get_all_command_bases()
			if not command[0] in command_bases:
				return str(command[0]) + ": Command not found!"
			else:
				if command_bases[command[0]][4]:
					command = shlex.split(original_command,posix=False)
				piped_commands.append(command)
		del commands
		end_of_pipe = len(piped_commands)
		pipe_iteration = 0
		piped_command = None
		terminal.pipe_in = None
		for command in piped_commands:
			if command[0] in command_bases:
				if piped_command != None and command_bases[command[0]][3] == False:
					return "Error: unable to pipe into " + command[0]
				else:
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
							pipe_iteration += 1
							if pipe_iteration == end_of_pipe:
								if output == True:
									if command_bases[command[0]][1][0] == "null":
										return command_bases[command[0]][1][0] == None
									if command_bases[command[0]][1][0] == "string":
										if response != None:
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
							else:
								piped_command = command[0]
								terminal.pipe_in = response
					except ValueError as e:
						return "Error: invalid parameter '" + str(e) + "' in " + command[0]
			else:
				return "Command not found!"




terminal = core()