// https://github.com/rizalasrul/c-basic-struct/blob/master/struct6.c
struct koordinat {
	int x, y;
};

void tukar_xy(struct koordinat *pos_xy) {
	int z;

	z = (*pos_xy).x;
	(*pos_xy).x = (*pos_xy).y;
	(*pos_xy).y = z;
  return ;
}
int main() {
	struct koordinat posisi;

	printf("Enter (x, y) : ");
	scanf("%d", &posisi.x);
	scanf("%d", &posisi.y);

  
	printf("Enter x, y = %d, %d\n", posisi.x, posisi.y);
	tukar_xy(&posisi);
	printf("x, y are = %d, %d\n", posisi.x, posisi.y);
  return 0;
}

