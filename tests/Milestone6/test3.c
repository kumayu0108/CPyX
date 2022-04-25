// https://stackoverflow.com/questions/27058275/how-do-i-declare-and-use-a-global-2d-array-in-c
int arr[32][32];

int main() {
  int i, j;
  for (i = 0; i < 32; i++) {
    for (j = 0; j < 32; j++) {
      arr[i][j] = i + j;
    }
  }

  for (i = 0; i < 32; i++) {
    for (j = 0; j < 32; j++) {
      printf("[%d,%d] = %d\n", i, j, arr[i][j]);
    }
  }
  return 0;
}