-- Industrial Embedded System Module: System_Module_098
-- Generated for Stress Testing
with Ada.Text_IO;
use Ada.Text_IO;

procedure System_Module_098 is
    type System_State is (Idle, Active, Error, Maintenance, Startup, Shutdown);
    type Sensor_Value is new Float range 0.0 .. 1000.0;
    
    type Control_Record is record
        State       : System_State := Idle;
        Pressure    : Sensor_Value := 0.0;
        Temperature : Sensor_Value := 25.0;
        Is_Valid    : Boolean := False;
        ErrorCode   : Integer := 0;
    end record;
    
    Current_Control : Control_Record;
    Safety_Threshold : constant Sensor_Value := 850.0;
    procedure Update_Diagnostics (Input : in Integer) is
        Local_Var : Integer := Input;
    begin
        if Local_Var > 100 then
            Current_Control.State := Active;
            Current_Control.Pressure := 500.0;
        elsif Local_Var < 0 then
            Current_Control.State := Error;
            Current_Control.ErrorCode := -1;
        else
            Current_Control.State := Idle;
        end if;
    end Update_Diagnostics;
begin
    -- Main Control Loop
    loop
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
            case Current_Control.State is
                when Idle =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Active =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Error =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Maintenance =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Startup =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
                when Shutdown =>
                    if Current_Control.Pressure > Safety_Threshold then
                        Current_Control.State := Error;
                        Current_Control.ErrorCode := 999;
                    else
                        Current_Control.Temperature := Current_Control.Temperature + 0.1;
                    end if;
            end case;
-- Update_Diagnostics(count); -- DELETED CALL
        if count > 1000 then exit; end if;
        count := count + 1;
    end loop;
end System_Module_098;