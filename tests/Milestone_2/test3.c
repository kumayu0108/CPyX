// INHERITENCE TESTING
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

int main()
{
   
}