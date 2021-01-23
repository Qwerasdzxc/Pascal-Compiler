int main() {
	char c;
	int lo;
	int hi;
	int d;
	scanf("%c", &c);
	lo = (c >= 65);
	hi = (c <= 90);
	if ((lo && hi)) {
		d = (c + 32);
	}
	else {
		d = (c - 32);
	}
	printf("%c", d);
}