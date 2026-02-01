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
        -- CHANGED: Threshold increased to 120.0
        if Alt > 120.0 then 
            Safe := False;
        else
            Safe := True;
        end if;
    end Check_Limits;
end Safety;
