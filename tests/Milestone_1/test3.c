/*
Testing struct , pointer  , Arithmetic operator
*/

struct student
{
    int age=9;
} ;

int main()
{
    // Structs 
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

    // Typecasting
    float y = (float)x/2;

    // Arrays
    int a[10], b[10][10];

    return 0;

}