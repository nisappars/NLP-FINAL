with Types; use Types;
with HAL;
package Sensors is
    procedure Read_Altitude(Alt : out Float_Type);
    procedure Read_Speed(Spd : out Float_Type);
end Sensors;
