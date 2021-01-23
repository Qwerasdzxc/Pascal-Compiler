int main() {
	int niz[100];
	int i;
	int j;
	int n;
	int temp;
	scanf("%d", &n);
	for (i = 1; i <= n; i ++) {
		scanf("%d", &niz[i]);
	}
	for (i = 1; i <= n; i ++) {
		for (j = (i + 1); j <= n; j ++) {
			if ((niz[i] <= niz[j])) {
				continue;
			}
			else {
				temp = niz[i];
				niz[i] = niz[j];
				niz[j] = temp;
			}
		}
	}
	for (i = 1; i <= n; i ++) {
		printf("%d%c", niz[i], 32);
	}
}