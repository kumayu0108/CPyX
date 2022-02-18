// Testing Virtaul Functions
class base {
public:
    void fun_1() { cout << "base-1\n"; }
    virtual void fun_2() { printf("base -1"); }
    virtual void fun_3() { printf("base -2"); }
    virtual void fun_4() { printf("base -4"); }
}
 
class derived : public base {
public:
    void fun_1() { printf("derived-1\n"); }
    void fun_2() { printf("derived-2\n"); }
    void fun_4(int x) { printf("derived-4\n"); }
}
int main()
{
    
}
