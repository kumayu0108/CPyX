// https://www.geeksforgeeks.org/memoization-1d-2d-and-3d/ 
// Returns length of LCS for X[0..m-1], Y[0..n-1]
int max(int a, int b)
{

    if (a>b)
    return a;
    return b;
}
 

int lcs(char* X, char* Y, char* Z, int m, int n, int o)
{
    // base case
    if (m == 0 || n == 0 || o == 0)
        return 0;
 
    // if equal, then check for next combination
    if (X[m - 1] == Y[n - 1] && Y[n - 1] == Z[o - 1]) {
 
        // recursive call
        int j=1 + lcs(X, Y, Z, m - 1, n - 1, o - 1);
        return j;
    }
    else {
 
        // return the maximum of the three other
        // possible states in recursion
        int k=max(lcs(X, Y, Z, m, n - 1, o),
        max(lcs(X, Y, Z, m - 1, n, o),
            lcs(X, Y, Z, m, n, o - 1)));
        return k;
    }
    return 0;
}
 
// Utility function to get max of 2 integers
// Driver Code
int main()
{
 
    char *X = "geeks";
    char *Y = "geeksfor";
    char *Z = "geeksforge";
    int m = 5;
    int n = 9;
    int o = 11;
    printf("%d",lcs(X, Y, Z, m, n, o));

    return 0;
}