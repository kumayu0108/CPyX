// https://www.tutorialspoint.com/cprogramming/c_recursion.htm
int fibonacci(int i) {

   if(i == 0) {
      return 0;
   }
	
   if(i == 1) {
      return 1;
   }
   return fibonacci(i-1) + fibonacci(i-2);
}

int  main() {

   int i;
	
   for (i = 0; i < 10; i++) {
      printf("%d ", fibonacci(i));
   }
	
   return 0;
}