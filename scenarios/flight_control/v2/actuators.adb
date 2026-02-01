with Types; use Types;
with HAL;
package Actuators is
    -- RENAMED: Move_Rudder -> Set_Rudder_Angle
    procedure Set_Rudder_Angle(Angle : in Float_Type);
end Actuators;

package body Actuators is
    procedure Set_Rudder_Angle(Angle : in Float_Type) is
    begin
        HAL.Write_Servo(1, Angle);
    end Set_Rudder_Angle;
end Actuators;
