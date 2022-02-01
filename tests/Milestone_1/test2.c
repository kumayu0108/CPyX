/*
Error testing 
*/
int main()
{
    int !k=1;        // (!) treated as negation token rather than part of identifier.
    int @=1;         // special symbol not allowed in variable name.
    int autoint = 1; // allowed variable name.
    scanf("%d", &autoint);
    
    #var2++;         // 
    return 0;
}