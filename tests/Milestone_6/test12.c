//  string check

int print(){
        char *s = "Arpit" ;
        int i = 0;
        while(s[i] != '\0')
        {
            printf("%c", s[i]) ;
            i++ ;
            if(i > 6)
                break ;
        }
        return 0 ;
}
int strcpy_stesting()
{
        char *a = "Subhro" ;
        char *b = (char*)malloc(14*sizeof(char)) ;
        strcpy(b , a) ;
        printf(" Subhro len is = %d\n", strlen(b)) ;
        return 0 ;
}

int main()
{
        print();
        strcpy_stesting();

        return 0;
}