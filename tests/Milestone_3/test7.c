int board[20],count;

int place(int row,int column)
{
int i;
for(i=1;i<=row-1;++i)
{
  if(board[i]==column)
   return 0;
  else
   if((board[i]-column)==(i-row))
    return 0;
}
 
return 1; 
}
void queen(int row,int n)
{
int column;
for(column=1;column<=n;++column)
{
  if(place(row,column))
  {
   board[row]=column; //no conflicts so place queen
   if(row!=n) 
    queen(row+1,n);
  }
}
}
int main()
{
int n = 8,i = 4,j = 3;
queen(1,n);
return 0;
}
 

