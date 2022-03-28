# CPyX

The directory structure is as follows : 
```
📦CPyX
 ┣ 📂bin
 ┃ ┗ 📜.gitkeep
 ┣ 📂docs
 ┃ ┗ 📜Milestone_1.pdf
 ┣ 📂plots
 ┃ ┣ 📜.gitkeep
 ┣ 📂src
 ┃ ┣ 📜lexer.py
 ┃ ┣ 📜parser.py
 ┣ 📂tests
 ┃ ┣ 📂Milestone_1
 ┃ ┃ ┣ 📜test1.c
 ┃ ┃ ┣ 📜test2.c
 ┃ ┃ ┣ 📜test3.c
 ┃ ┃ ┣ 📜test4.c
 ┃ ┃ ┣ 📜test5.c
 ┃ ┃ ┣ 📜test6.c
 ┃ ┃ ┗ 📜test7.c
 ┃ ┗ 📂Milestone_2
 ┃ ┃ ┣ 📜test1.c
 ┃ ┃ ┣ 📜test2.c
 ┃ ┃ ┣ 📜test3.c
 ┃ ┃ ┣ 📜test4.c
 ┃ ┃ ┣ 📜test5.c
 ┃ ┃ ┣ 📜test6.c
 ┃ ┃ ┗ 📜test7.c
 ┃ ┗ 📂Milestone_3
 ┃ ┃ ┣ 📜test1.c
 ┃ ┃ ┣ 📜test2.c
 ┃ ┃ ┣ 📜test3.c
 ┃ ┃ ┣ 📜test4.c
 ┃ ┃ ┣ 📜test5.c
 ┃ ┃ ┣ 📜test6.c
 ┃ ┃ ┗ 📜test7.c
 ┣ 📜Makefile
 ┣ 📜README.md
 ┣ 📜requirements.txt
```
Install required pip packages using the requirements.txt file
```
pip install -r ./requirements.txt
```

Steps to build and run lexer:
Pass all the files to be analyzed by the lexer

```
$ python3 src/lexer.py test_case_1.c test_case_2.c .... test_case_n.c
```

To run lexer on predefined test cases for Milestone 1 use 
```
$ make testM1
```

Steps to build and run parser:
Pass all the files to be analyzed by the parser

```
$ python3 src/parser.py test_case_1.c test_case_2.c .... test_case_n.c
```

To run parser on pre defined test cases, run 
```
$ make testM2
```
output of parse.py would be symbol_table_dump.csv, symbol_table_dump.json and graph1.dot which is the dot file generated that contains the AST.

To clean all the temporary files, run
```
$ make clean
```
