with Types; use Types;
with HAL;
package Actuators is
    procedure Move_Rudder(Angle : in Float_Type);
end Actuators;

package body Actuators is
    procedure Move_Rudder(Angle : in Float_Type) is
    begin
        HAL.Write_Servo(1, Angle);
    end Move_Rudder;
end Actuators;
