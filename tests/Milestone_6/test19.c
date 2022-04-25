// function overloading 

void type_check(int a)
{
    printf(" an int\n") ;
    return ;
}
void type_check(float a)
{
    printf(" a float\n") ;
    return ;
}

void type_check(int a , int b)
{
    printf(" int and int\n") ;
    return ;
}
void type_check(int a , float b)
{
    printf(" int and float\n") ;
    return ;
}

void type_check(float a , int b)
{
    printf(" float and int\n") ;
    return ;
}

void type_check(float a , float b)
{
    printf(" float and float\n") ;
    return ;
}

void type_check(int a , int b , int c)
{
    printf("I have 3 args\n") ;
    return ;
}
int main()
{
    int a = 5 ;
    float b = 2 ;

   



    type_check(a , a , a) ;
    type_check(a , b , a) ;
    type_check(b , a , a) ;
    type_check(a , a , b) ;
    type_check(b , b , b) ;
    printf("\n") ;
    type_check(a) ;
    type_check(b) ;

    printf("\n") ;

    type_check(a , a) ;
    type_check(a , b) ;
    type_check(b , a) ;
    type_check(b , b) ;

    return 0 ;
}