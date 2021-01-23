var
	a : array[1..100] of integer;
	i, n, max, tmax : integer;

begin
	max := -32768;
	tmax := 0;

	readln(n);

	for i := 1 to n do
	begin
		read(a[i]);
	end;

	for i := 1 to n do
	begin
		tmax := tmax + a[i];

		if tmax > max then
		begin
			max := tmax;
		end;

		if tmax < 0 then
		begin
			tmax := 0;
		end;
	end;

    write(max);
end.
