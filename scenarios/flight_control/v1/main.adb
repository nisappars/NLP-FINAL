with Types; use Types;
with Sensors;
with Actuators;
with Safety;
with Navigation;
with Logger;

procedure Main is
    Is_Safe : Boolean;
    Alt : Float_Type;
    Start, Dest : Coordinate_Type;
    ETA : Float_Type;
begin
    Sensors.Read_Altitude(Alt);
    Safety.Check_Limits(Is_Safe);
    
    if Is_Safe then
        Navigation.Calculate_Route(Start, Dest, ETA);
        Actuators.Move_Rudder(10.0);
    else
        Logger.Log_Event("Unsafe condition detected");
        Actuators.Move_Rudder(0.0);
    end if;
end Main;
