testM1:	src/lexer.py
	@echo "Running pre defined test cases"
	@for i in `seq 1 7`; do \
		python3 src/lexer.py tests/Milestone_1/test$$i.c ; \
	done
	
testM2: src/parser.py
	@echo "Running pre defined test cases for parser"
	@for i in `seq 1 8`; do \
		python3 src/parser.py tests/Milestone_2/test$$i.c ; \
	done
	
clean: 
	rm -f testM2 *.dot 
	rm -f testM2 ./plots/*.png
	rm -f testM2 ./src/parsetab.py
