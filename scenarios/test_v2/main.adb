procedure Main is
   X : Integer := 0;

   procedure Safety_Check is
   begin
      -- Critical safety logic
      null;
   end Safety_Check;

   procedure Old_Logic is
   begin
      -- Safety check REMOVED!
      -- Logic changed
      if X > 0 then
         null;
      end if;
   end Old_Logic;

   procedure Renamed_Logic is
   begin
      -- Identical logic to To_Be_Renamed
      X := X + 1;
      X := X * 2;
   end Renamed_Logic;

begin
   Old_Logic;
   Renamed_Logic;
end Main;
