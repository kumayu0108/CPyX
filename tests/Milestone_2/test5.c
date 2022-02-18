int main()
{
    int t;
    scanf("%d", &t) ;
    while (t--)
    {
        int n;
        scanf("%d", &n);
        int a1;
        int carspd[n];
        for (a1 = 0; a1 < n; a1++)
        {
            scanf("%d", &carspd[a1]);
        }
        int x = 1;
        for (a1 = 0; a1 < n - 1; a1++)
        {
            if (carspd[a1] < carspd[a1 + 1])
            {
                carspd[a1] = carspd[a1 + 1];
            }
            else if (carspd[a1] >= carspd[a1 + 1])
            {
                x++;
            }
        }
        printf("%d\n", x);
    }

    return 0;
}