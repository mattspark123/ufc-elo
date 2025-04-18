import os


#Open the file, read last line to see where we left off
def findLastLine(filename):
	if os.path.exists(filename) and os.path.getsize(filename) > 1:
		with open(filename, 'rb') as file:  # Open in binary mode
		    file.seek(-2, 2)  # Move to the second-to-last byte
		    while file.read(1) != b'\n':  # Keep reading backward until a newline
		        file.seek(-2, 1)  # Move one byte back
		    last_line = file.readline().decode()  # Read the last line
		    return last_line
	else:
		last_line = 0
		return last_line

def deleteLastLine(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 1:
        with open(filename, 'rb+') as file:
            file.seek(-2, os.SEEK_END)  # Move to the second-to-last byte
            while file.read(1) != b'\n':  # Move backward until a newline is found
                file.seek(-2, os.SEEK_CUR)  # Move one byte back
            file.truncate()  # Truncate the file at the current position