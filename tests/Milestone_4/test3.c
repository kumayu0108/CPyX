
int global_arr[100][100];
int ackermann_recursion(int m, int n)
{
    if (global_arr[m][n] != -1)
        return global_arr[m][n];
    if (m == 0)
        return n + 1;

    if (n == 0)
    {
        return global_arr[m][n] = ackermann_recursion(m - 1, 1);
    }

    return global_arr[m][n] = ackermann_recursion(m - 1, ackermann_recursion(m, n - 1));
}
int main()
{
    int i, j;
    for (i = 0; i < 100; i++)
        for (j = 0; j < 100; j++)
            global_arr[i][j] = -1;
    return 0;
}
