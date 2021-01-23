procedure check_arm(x, cj, cd, cs: integer);
	var
		arm: boolean;

	begin
		if x < 0 then
		begin
			exit;
		end;

		arm := x = cj * cj * cj + cd * cd * cd + cs * cs * cs;

		if arm then
		begin
			write('DA');
		end
		else
		begin
			write('NE');
		end;
	end;

var
	broj, cj, cd, cs: integer;

begin
	readln(broj);

	cj := broj mod 10;
	cd := (broj div 10) mod 10;
	cs := (broj div 100) mod 10;

	check_arm(broj, cj, cd, cs);
end.