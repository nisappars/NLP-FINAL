with Types; use Types;
with Sensors;
package Safety is
    procedure Check_Limits(Safe : out Boolean);
end Safety;

package body Safety is
    procedure Check_Limits(Safe : out Boolean) is
        Alt : Float_Type;
        Spd : Float_Type;
    begin
        Sensors.Read_Altitude(Alt);
        Sensors.Read_Speed(Spd);
        if Alt > 100.0 then 
            Safe := False;
        else
            Safe := True;
        end if;
    end Check_Limits;
end Safety;
