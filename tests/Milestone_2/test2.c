// CLASS TESTING
// class abc{
//     private:
//         friend a;
//         int x,y,z;
//     public:
//         int add(int p,int q){
//             return p+q;
//         }
//         abc(int num){
//             x = num;
//             y = num;
//             z = num;
//         }
// };
int gcd(int a, int b)
{
    // Everything divides 0
    if (a == 0)
        return b;
    if (b == 0)
        return a;

    // base case
    if (a == b)
        return a;

    // a is greater
    if (a > b)
        return gcd(a - b, b);
    return gcd(a, b - a);
}

// Driver program to test above function
int main()
{
    int a = 98, b = 56;
    printf("GCD of %d and %d is %d ", a, b, gcd(a, b));
    return 0;
}
