python3 ./src/main.py "$1"
nasm -f elf32 out.asm
gcc -m32 -no-pie out.o -lm
./a.out 
