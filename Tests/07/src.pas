var
	i, j, n: integer;

begin
	readln(n);

	for i := n downto 1 do
	begin
		for j := n - i downto 1 do
		begin
			write(' ');
		end;

		for j := 2 * i - 1 downto 1 do
		begin
			write('*');
		end;

		writeln();
	end;
end.
