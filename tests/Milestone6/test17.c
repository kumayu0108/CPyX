
// global assignment , struct 
struct point{
    int x, y;
    int z[5];
    char c;
};

struct point p = {2, 3, {2,4,8,16}, 'c'};
int global_Struct_check()
{
        int i =0;
        printf("%d %d\n", p.x, p.y);
        for(i = 0; i<5; i++)    printf("%d ", p.z[i]);
        printf("\n%c\n", p.c);
        return 0;
}
        int val[100][100] ;

int global_assign()
{

            int i = 0 , j = 0 ;
            for(; i < 100 ; i++)
            {
                for( ; j < 100 ; j++)
                    val[i][j] = -1 ;
            }
            return 0 ;
        
}

int calc_odd(int) ;
int calc_even(int) ;

int val2[10] ;



int calc_odd(int n)
{
    printf("n = %d\n", n) ;
    if(n%2 == 0)
        return -1 ;
    if(val2[n] != -1)
        return val[n] ;
    return val2[n] = 2*n + calc_even(n-1);
    
}
int calc_even(int n)
{
    printf("n = %d\n", n) ;
    if(n%2)
        return -1 ;
    if(n == 0)
    val2[n]=0;
        return val[n] ;
    if(val2[n] != -1)
        return val[n] ;
         val2[n] = n/2 + calc_odd(n-1);
    return val2[n] ;
    
}


int main()
{
    
    int i = 0 ;
    for(i = 0 ; i < 10 ; i++)
    {
        val2[i] = -1 ;
    }
    calc_odd(9) ;
    printf("\n") ;
    for(i = 0 ; i < 10 ; i++)
    {
        printf("i = %d, val = %d\n", i , val2[i]) ;
    }
    printf("\n") ;
    calc_even(8) ;

    global_Struct_check();
    global_assign();
    return 0 ;
}