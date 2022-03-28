struct a
{
    int ca;
    int cb;
};



// f(g(h(1, c, b, d), d), f){ }

int main()
{
    int int s = 10;
    a = 2;               //should give undeclared error
    int k = func1(d, c); //undeclared error
    struct b
    {
        int k;
    };
    struct a* l;
    l->cb = 1; //undeclared error
    struct a obj1;
    struct b obj2;
    obj1 = obj2;
    return 0;
}
