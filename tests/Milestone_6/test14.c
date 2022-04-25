// Quick Sort 
void swap(int *a , int *b)
{
    int c = *a ;
    *a = *b ;
    *b = c ;
    return ;
}

void print_arr(int arr[] , int left , int right)
{
    int i = left ;
    for(; i <= right ; i++)
    {
        printf("%d ", arr[i]) ;
    }
    printf("\n") ;
    return ;
}

void Quicksort(int arr[] , int left , int right)
{
    int pivot = arr[right] , pos = left ;
    int i = 0 ;
    int curr_pos = 0 , ind = right;

    if(left >= right)
        return ;

    printf("before : ") ;
    print_arr(arr , left , right) ;
    
    for(i = left ; i <= right ; i++)
    {
        if(arr[i] < pivot)
            pos++ ;
    }

    curr_pos = left ;
    swap(&arr[right] , &arr[pos]) ;
    for(ind = right ; ind > pos ; ind--)
    {
        if(arr[ind] < pivot)
        {
            while(arr[curr_pos] < pivot)
                curr_pos++ ;
            swap(&arr[curr_pos] , &arr[ind]) ;
        }
    }

    printf("after : ") ;
    print_arr(arr , left , right) ;

    Quicksort(arr , left , pos-1) ;
    Quicksort(arr , pos+1 , right) ;
    // return;
}

int main()
{
    int n = 6 ;
    int arr[6] ;
    arr[0] = 0 , arr[1] = 5 , arr[2] = 2 , arr[3] = 1 , arr[4] = 4 , arr[5] = 5 ;
    printf("Before Quicksort : ") ;
    print_arr(arr , 0 , 5) ;
    Quicksort(arr , 0 , 5) ;
    printf("After Quicksort : ") ;
    print_arr(arr , 0 , 5) ;
    return 0 ;
}