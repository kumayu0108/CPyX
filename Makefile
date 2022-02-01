testM1:	src/lexer.py
	@echo "Running pre defined test cases"
	@for i in `seq 1 7`; do \
		python3 src/lexer.py tests/Milestone_1/test$$i.c ; \
	done