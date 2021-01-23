int main() {
	int a;
	int b;
	scanf("%d%d", &a, &b);
	printf("%d%c%d%c%d%c%d%c%d", (a + b), 32, (a - b), 32, (a * b), 32, (a / b), 32, (a % b));
}