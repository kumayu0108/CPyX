struct Point
{
    int x, y, z;
};

int main()
{
    // Examples of initialization using designated initialization
    struct Point p1 ;
    struct Point p2 ;

    printf("x = %d, y = %d, z = %d\n", p1.x, p1.y, p1.z);
    printf("x = %d", p2.x);
    return 0;
}