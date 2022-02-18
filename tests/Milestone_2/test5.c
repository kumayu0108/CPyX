// Object Declaration Testing
class abc{
    private:
        friend a;
        int x,y,z;
    public:
        int add(int p,int q){
            return p+q;
        }
        abc(int num){
            x = num;
            y = num;
            z = num;
        }
        ~abc(){
            printf("bye!!");
        }
}

class pqr : private abc {
    private :
        int p,q,r;
    public:
        int show(int num1){
            printf("%d",num1);
        }
}

int main()
{
    string x = "cs335a";
    class_obj abc class_1;
    return 0;
}