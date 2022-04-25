import parser2
import sys
import codegen

if(len(sys.argv) <= 1):
	print("Incorrect Usage")
	print('Usage: python3 run_compiler.py [file name]')
	exit()

file = open(sys.argv[1])
code = file.read()
if __name__ == '__main__':
	parser2.runmain(code)
	codegen.runmain()