/* scope test */
int main()
{
    {
        {
            {
                printf("inner scope 3");
            }
        printf("inner scope 2");
        }
       printf("inner scope 1");
    }
}