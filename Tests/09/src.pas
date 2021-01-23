var
	niz : array[1..100] of integer;
	i, j, n, temp: integer;

begin
	readln(n);

	for i := 1 to n do
	begin
		read(niz[i]);
	end;

	for i := 1 to n do
	begin
		for j := i + 1 to n do
		begin
			if niz[i] <= niz[j] then
			begin
				continue;
			end
			else
			begin
				temp := niz[i];
				niz[i] := niz[j];
				niz[j] := temp;
			end;
		end;
	end;

	for i := 1 to n do
	begin
		write(niz[i], ' ');
	end;
end.
