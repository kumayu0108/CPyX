/*
Testing struct , pointer  , Arithmetic operator
*/

struct student
{
    int age=9;
} ;

int main()
{
    struct student* var;
    printf("age is %d",var->age);
    var->age=5;

    int * p;
    *p=5;
    int *y=9;
    printf("%d",*p);
    printf("%d",*y);


    int x=1,y=3;
    x=x++ - --y;
    x=++x + ++y;
    x=++x+++x;
    x/=4;
    x*=x;
    x%=++x;
    x+=3;
    x-=5;
    x<<=4;
    x>>=5;


    return 0;

}