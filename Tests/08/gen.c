int jeProst(int n) {
	int i;
	if ((n <= 1)) {
		return 0;
	}
	for (i = (n / 2); i >= 2; i --) {
		if (((n % i) == 0)) {
			return 0;
		}
	}
	return 1;
}
int main() {
	int n;
	int i;
	int s;
	scanf("%d", &n);
	i = 0;
	s = 1;
	do {
		if (jeProst(s)) {
			i = (i + 1);
			if ((i == n)) {
				break;
			}
		}
		s = (s + 1);
	} while( !(0) );
	printf("%d\n", s);
}