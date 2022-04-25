// while multidimensionalArray, break checking
void break_check()
{
        int x = 4 , y = 5 ;
        while(x > 0)
        {
            y = 5 ;
            while(y > 0)
            {
                if(x == 2 && y == 3)
                    break ;
                printf("x = %d, y = %d\n", x , y) ;
                y-- ;
            }
            x-- ;
        }
}
int main()
{
    int arr[2][2][2][2] ;
    int i , j , k , l;
    for(i = 0 ; i < 2 ; i++)
        for(j = 0 ; j < 2 ; j++)
            for(k = 0 ; k < 2 ; k++)
                for(l = 0 ; l < 2 ; l++)
                    arr[i][j][k][l] = i+j+k+l;

    i = 1 , j = 1 , k = 1 , l = 1 ;
    while(i >= 0)
    {
        j = k = l = 1 ;
        while(j >= 0)
        {
            k = l = 1 ;
            while(k >= 0)
            {
                l = 1 ;
                while(l >= -1)
                {
                    printf("i = %d, j = %d , k = %d , l = %d , val = %d\n", i , j , k , l , arr[i][j][k][l]) ;
                    l-- ;
                    if(l < 0)
                        break ;
                }
                k-- ;
            }
            j-- ;
        }
        i-- ;
    }

    break_check();


    return 0 ;        
}