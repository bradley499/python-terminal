# core.py

import os
import json

class terminal_system():
    def __init__(self):
        self.set_all_command_bases()
        self.dir = False
        self.set_cwd(os.getcwd())
    def set_all_command_bases(self):
        self.command_bases = {"pwd":[self.get_cwd,["string"]],"ls":[self.ls,["join"," "]],"hostname":[self.get_hostname,["string"]],"cd":[self.change_directory,["string/void"]],"mkdir":[self.create_directory,["join/void","\n"]],"rmdir":[self.remove_directory,["join/void","\n"]]}
        return True

    def get_all_command_bases(self):
        self.set_all_command_bases()
        return self.command_bases

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
                else:
                    raise ValueError(arg)
        files = files + os.listdir(self.get_cwd())
        list_files = []
        for x in range(len(files)):
            if not show_hidden:
                if files[x][0] == ".":
                    continue

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
        try:
            with open("device.json","r") as device_details:
                try:
                    device_details = json.loads(device_details.read())
                    return device_details["name"]
                except:
                    return ""
        except:
            return ""
        return ""

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
            print(dir_del_default_string)
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
            print(small_relative_dir_creation)
            print(dir_del_sub_name + " ##### " + "/".join(small_relative_dir_creation[1:]))
            print(dir_string)
            print(["/".join(dir_del_default_string)])
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
                print("_____________________________")
                print(small_relative_dir_creation)
                for dir_del_parent in dir_del_tree:
                    directory_contents = self.ls(["-a"])
                    if directory_contents != [".",".."]:
                        response.append("rmdir: failed to remove '/" + "/".join(directory_parent_naming[dir_deletion_iteration]) + "' as directory is not empty")
                    else:
                        self.change_directory([".."])
                        if verbose:
                            response.append("rmdir: removing directory '" + small_relative_dir_creation[dir_deletion_iteration] + "'")
                        print(self.get_cwd())
                        print("Parents children: ", self.ls(["-a"]))
                        print("Deleting: ", dir_del_parent);
                        print("Child verified existance: ", dir_del_parent in self.ls(["-a"]))
                        print("existance: ", os.path.exists(dir_del_parent))
                        os.rmdir(self.get_cwd() + "/" + dir_del_parent)
                    dir_deletion_iteration+=1
                    if self.get_cwd() == os.path.abspath(dir_string):
                        break;
                    elif not delete_directory_parent:
                        break;
            else:
                print(small_relative_dir_creation)
                if dir_del == "":
                    dir_del = "/"
                response.append("rmdir: failed to remove '" + dir_del + "' as no file or directory exists1")
        current_base_dir = "/" + "/".join(current_base_dir)
        if self.get_cwd() != current_base_dir:
            self.change_directory([current_base_dir])
        return response




        # small_relative_dir_creation first relative directory naming structure (duplicates occur)!




        

def terminal_parse(command = "", output = True, terminal = ""):
    if terminal == False:
        return "Error: no terminal handler was provided"
    if command.strip() == "":
        return ""
    else: 
        command = command.strip().split(" ")
        command_bases = terminal.get_all_command_bases()
        if command[0] in command_bases:
            try:
                response = command_bases[command[0]][0](command[1:])
                if output == True:
                    if command_bases[command[0]][1][0] == "null":
                        return command_bases[command[0]][1][0] == None
                    if command_bases[command[0]][1][0] == "string":
                        return str(response)
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




terminal = terminal_system()

for x in range(15):
    response = (terminal_parse(input(terminal.get_hostname() + ":" + terminal.get_cwd() + "$ "),True,terminal))
    if not response in ["",None] :
        print(response)