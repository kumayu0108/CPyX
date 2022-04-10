// R = 3;
// C = 3;
int min(int x, int y, int z)
{
    if (x < y && x < z)
        return x;
    else if (x < y && x < z)
        return z;
    else if (y < z)
        return y;
    else
        return z;
    return 0;
}

int minCost(int cost[3][3], int m, int n)
{
    if (n < 0 || m < 0)
        return 1000000;
    else if (m == 0 && n == 0)
        return cost[m][n];
    else
        return cost[m][n] + min(minCost(cost, m - 1, n - 1),
                                minCost(cost, m - 1, n),
                                minCost(cost, m, n - 1));
    return 0;
}

// /* A utility function that returns minimum of 3 integers */

/* Driver program to test above functions */
int main()
{
    int cost[3][3] = {{1, 2, 3},
                      {4, 8, 2},
                      {1, 5, 3}};
    
    return 0;
}
