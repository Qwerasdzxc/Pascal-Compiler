var
	a1, b1, a2, b2, p1, p2: real;

begin
	readln(a1, b1, a2, b2);

	p1 := a1 * b1 / 2;
	p2 := a2 * b2 / 2;

	if p1 > p2 then
	begin
		write('1');
	end
	else
	begin
		if p1 < p2 then
		begin
			write('2');
		end
		else
		begin
			write('0');
		end;
	end; 
end.
