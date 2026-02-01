with Types; use Types;
with Sensors;
with Actuators;
with Safety;
with Navigation;
with Logger;
with AI_Pilot; -- NEW dependency

procedure Main is
    Is_Safe : Boolean;
    Alt : Float_Type;
    Start, Dest : Coordinate_Type;
    ETA : Float_Type;
begin
    Sensors.Read_Altitude(Alt);
    Safety.Check_Limits(Is_Safe);
    
    if Is_Safe then
        -- CHANGED: Updated signature
        Navigation.Calculate_Route(Start, Dest, 1.0, ETA);
        -- RENAMED: Call updated
        Actuators.Set_Rudder_Angle(10.0);
        
        -- NEW: Call to AI
        AI_Pilot.Auto_Fly;
    else
        Logger.Log_Event("Unsafe condition detected");
        Actuators.Set_Rudder_Angle(0.0);
        
        -- CHANGED: Extra logging
        Logger.Log_Event("Initiating Emergency Protocol");
    end if;
end Main;
