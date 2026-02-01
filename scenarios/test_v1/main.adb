procedure Main is
   X : Integer := 0;

   procedure Safety_Check is
   begin
      -- Critical safety logic
      null;
   end Safety_Check;

   procedure Old_Logic is
   begin
      if X > 0 then
         Safety_Check;
      end if;
   end Old_Logic;

   procedure To_Be_Renamed is
   begin
      -- Some "complex" logic to fingerprint
      X := X + 1;
      X := X * 2;
   end To_Be_Renamed;

begin
   Old_Logic;
   To_Be_Renamed;
end Main;
