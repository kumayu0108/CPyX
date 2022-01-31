testM1:	lexer.py
	@echo "Running pre defined test cases"
	@for i in `seq 1 8`; do \
		python3 lexer.py tests/Milestone_1/test$$i.c ; \
		echo "______________________________________________________________________" ; \
	done