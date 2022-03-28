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
	
plot : graph1.dot
	@dot -x -Goverlap=scale -Tpng ./graph1.dot > ./plots/graph_out.png
	
clean: 
	rm -f ./bin/*.dot 
	rm -f ./plots/*.png
	rm -f ./src/parsetab.py
	rm -f ./src/*.out
