
// https://www.geeksforgeeks.org/dynamically-allocate-2d-array-c/
int main()
{
	int r = 3, c = 4;

	int* ptr = (int *)malloc((r * c) * sizeof(int));
	int i;
	/* Putting 1 to 12 in the 1D array in a sequence */
	for (i = 0; i < r * c; i++){
		ptr[i] = i + 1;
	}

	/* Accessing the array values as if it was a 2D array */
	for (i = 0; i < r; i++) {
		for (int j = 0; j < c; j++){
			printf("%d ", ptr[i * c + j]);
		}
		printf("\n");
	}

	return 0;
}
