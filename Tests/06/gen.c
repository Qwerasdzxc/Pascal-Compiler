int main() {
	float a1;
	float b1;
	float a2;
	float b2;
	float p1;
	float p2;
	scanf("%f%f%f%f", &a1, &b1, &a2, &b2);
	p1 = ((a1 * b1) / 2);
	p2 = ((a2 * b2) / 2);
	if ((p1 > p2)) {
		printf("%c", 49);
	}
	else {
		if ((p1 < p2)) {
			printf("%c", 50);
		}
		else {
			printf("%c", 48);
		}
	}
}