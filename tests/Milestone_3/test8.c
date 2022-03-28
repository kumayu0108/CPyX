int recurse()
{
    int x = recurse() ;
    return 5;
}
int main()
{
    recurse();
    return 0 ;
}
