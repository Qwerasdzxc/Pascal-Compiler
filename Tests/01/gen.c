int main() {
	float a;
	float b;
	scanf("%f%f", &a, &b);
	printf("%.2f%c%.2f%c%.2f", (a + b), 32, (a - b), 32, (a / b));
}