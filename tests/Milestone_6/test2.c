//  2d array passing 
void pass2d(int *arr , int n , int m)
{
    int i , j ;
    for(i = 0 ; i < n ; i++)
    {
        for(j = 0 ; j < m ; j++)
            printf("%d ", (*(arr + i*m + j))) ;
        printf("\n") ;
    }
}
int main()
{
    int n = 2 , m = 2 ;
    int arr[2][2] ;
    int i , j ;
    for(i = 0 ; i < 2 ; i++)
        for(j = 0 ; j < 2 ; j++)
            arr[i][j] = (i+j) ;
    pass2d((int *)arr , 2 , 2) ;
    return 0 ; 
}
