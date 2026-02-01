package body Sensors is
    procedure Read_Altitude(Alt : out Float_Type) is
    begin
        HAL.Read_Sensor(1, Alt);
    end Read_Altitude;

    procedure Read_Speed(Spd : out Float_Type) is
    begin
        HAL.Read_Sensor(2, Spd);
    end Read_Speed;
end Sensors;
