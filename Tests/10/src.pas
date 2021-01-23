var
	a, b, c : array[1..100] of integer;
	n, ai, bi, ci, i: integer;

begin
    bi := 1;
	ci := 1;

	readln(n);
	
	for ai := 1 to n do
	begin
		read(a[ai]);
	end;

	for ai := 1 to n do
	begin
		if a[ai] mod 2 = 0 then
		begin
			b[bi] := a[ai];
			bi := bi + 1;
		end
		else
		begin
			c[ci] := a[ai];
			ci := ci + 1;
		end;
	end;

	for i := 1 to bi - 1 do
	begin
		write(b[i], ' ');
	end;

	writeln();

	for i := 1 to ci - 1 do
	begin
		write(c[i], ' ');
	end;
end.
