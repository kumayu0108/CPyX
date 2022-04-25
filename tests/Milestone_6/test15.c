// Pointer testing


void change(int **x , int* y)
{
    *x = y ;
    return ;
}

void print(char c)
{
    printf("%c", c) ;
}
int post(int* a)
{
    return (*a)++ ;
}
void multi_pointer()
{
        int a, *p, **ptr, ***pt, ****ps, z;
        a=4;
        p = &a;
        ptr = &p;
        pt = &ptr;
        ps = &pt;

        printf("%d\n", ****ps);

        a = 8;

        printf("%d\n", ****ps);
        return ;
}

int main()
{

   char greeting[6] = {'H', 'e', 'l', '\0', 'o', '\0'};
   char *s = greeting ;
   printf("%s\n", s);
   
    int y = 4 ;
    int* x = &y ;
    int z = 0 ;
    change(&x , &z) ;
    printf("Enter a number:\n");
    printf("%d\n", z);
    int a = 5 ;
    printf("post = %d\n", post(&a)) ;
    printf("new_value of a = %d\n", a) ;

    multi_pointer();
    return 0 ;
}