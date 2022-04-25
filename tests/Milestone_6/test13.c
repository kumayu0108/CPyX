float eps = 1e-4 ;
void get_val(float* val, int a , int b , float x)
{
    (*val) = (a*x + b) ;
    return ;
}

float get_val_quad(int a , int b , int c , float x)
{
    return (a*x*x + b*x + c) ;
}
int main()
{
    int a = 1 , b = -10 , c = 25 ;
    float x[100] ;
    int i = 1 ;
    int iter = 30;
    float curr_val_diff , curr_val_func ;
    x[0] = 0 ;
    for(i ; i < iter ; i++)
    {
        get_val(&curr_val_diff , 2*a , b , x[i-1]) ;
        curr_val_func = get_val_quad(a , b , c , x[i-1]) ;

        x[i] = x[i-1] ;
        if(curr_val_func < eps && curr_val_func > -eps)
            continue ;
        if(curr_val_diff < eps && curr_val_diff > -eps)
            continue ;

        printf("i = %d, diff = %f, val = %f\n", i ,curr_val_diff , curr_val_func) ;
        
        x[i] = x[i-1] - (curr_val_func) / curr_val_diff ;
    }
    printf("root = %f\n", x[iter-1]) ;

    return 0 ;

}