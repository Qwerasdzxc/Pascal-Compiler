function jeProst(n: integer): boolean;
	var
		i: integer;
	
	begin
		if n <= 1 then
		begin
			exit(false);
		end;

		for i := n div 2 downto 2 do
		begin
			if n mod i = 0 then
			begin
				exit(false);
			end;
		end;

		exit(true);
	end;

var
	n, i, s: integer;

begin
	readln(n);

	i := 0;
	s := 1;

	repeat
		if jeProst(s) then
		begin
			i := i + 1;

			if i = n then
			begin
				break;
			end;
		end;

		s := s + 1;
	until false;

	writeln(s);
end.
