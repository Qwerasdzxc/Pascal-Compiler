var
	c: char;
    lo, hi: boolean;
    d: integer;

begin
	readln(c);

    lo := ord(c) >= ord('A');
    hi := ord(c) <= ord('Z');

	if lo and hi then
	begin
		d := ord(c) + 32;
	end
	else
	begin
		d := ord(c) - 32;
	end;

    write(chr(d));
end.
