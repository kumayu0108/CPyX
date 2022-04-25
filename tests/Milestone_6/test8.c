// Function to sort the numbers using pointers
int sort(int n, int ptr[])
{
    int i, j, t;
  
    // Sort the numbers using pointers
    for (i = 0; i < n; i++) {
  
        for (j = i + 1; j < n; j++) {
  
            if (*(ptr + j) < *(ptr + i)) {
  
                t = *(ptr + i);
                *(ptr + i) = *(ptr + j);
                *(ptr + j) = t;
            }
        }
    }
  
    // print the numbers
    for (i = 0; i < n; i++)
        printf("%d ", *(ptr + i));

        return 0;
}
  
// Driver code
int main()
{
    int n = 5;
    int arr[5] ;
    arr[0]=0;
    arr[1]=23;
    arr[2]=14;
    arr[3]=12;
    arr[4]=9;
 
    sort(n, arr);
  
    return 0;
}