with Types; use Types;
package HAL is
    procedure Read_Sensor(Id : Integer; Val : out Float_Type);
    procedure Write_Servo(Id : Integer; Val : in Float_Type);
end HAL;
