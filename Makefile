testM1:	src/lexer.py
	@echo "Running pre defined test cases"
	@for i in `seq 1 7`; do \
		python3 src/lexer.py tests/Milestone_1/test$$i.c ; \
	done
	
testM2: src/parser.py
	@echo "Running pre defined test cases for parser"
	@python3 src/parser.py tests/Milestone_2/test1.c
	@sfdp -x -Goverlap=scale -Tpng ./bin/outfile.dot > ./plots/graph_out.png

testM3: src/parser.py
	@echo "Running pre defined test cases for parser"
	@for i in `seq 1 8`; do \
		python3 src/parser.py tests/Milestone_3/test$$i.c ; \
	done
	
testM6: src/run_compiler.py
	@echo "Running pre defined test cases for our compiler"
	@for i in `seq 1 8`; do \
		python3 src/run_compiler.py tests/Milestone_6/test$$i.c ; \
		gcc -m32 -no-pie out.asm -lm ; \
		./a.out > codeOutput.txt ; \
	done
plot : graph1.dot
	@dot -x -Goverlap=scale -Tpng ./graph1.dot > ./plots/graph_out.png
	
clean: 
	rm -f ./bin/*.dot 
	rm -f ./plots/*.png
	rm -f ./src/parsetab.py
	rm -f ./src/*.out
