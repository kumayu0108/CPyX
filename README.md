# CPyX

<!-- Add a README file in <TOP>/ with a brief description of your project and the steps to build and run it. -->

The directory structure is as follows : 
```
📦CPyX
 ┣ 📂bin
 ┃ ┗ 📜.gitkeep
 ┣ 📂docs
 ┃ ┗ 📜Milestone_1.pdf
 ┣ 📂src
 ┃ ┗ 📜lexer.py
 ┣ 📂tests
 ┃ ┣ 📂Milestone_1
 ┃ ┃ ┣ 📜test1.c
 ┃ ┃ ┣ 📜test2.c
 ┃ ┃ ┣ 📜test3.c
 ┃ ┃ ┣ 📜test4.c
 ┃ ┃ ┣ 📜test5.c
 ┃ ┃ ┣ 📜test6.c
 ┃ ┃ ┗ 📜test7.c
 ┣ 📜Makefile
 ┣ 📜requirements.txt
 ┗ 📜README.md
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
