// Binary search iterative

void binSearch(int array[] , int l , int r , int val)
{   
    int middle ;
    printf("l = %d, r = %d\n", l, r);
    if(l > r)
    {
        printf("not present\n") ;
        return ;
    }
    middle = (l+r)/2 ;
    if(array[middle] == val)
    {
        printf("ans = %d\n", middle) ;
        return ;
    }
    if(array[middle] > val)
        return binSearch(array , l , middle-1 , val) ;
    return binSearch(array , middle+1 , r , val) ;
}
int main()
{
    int array[500] ;
    int i = 0 ; 
    for(i = 0 ; i < 500 ; i++)
        array[i] = i+1 ;
    binSearch(array , 0 , 499 , 122) ;
    binSearch(array , 0 , 499 , 111) ;
    binSearch(array , 0 , 499 , 0) ;
    return 0 ;
}