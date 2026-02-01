package Types is
    type Float_Type is digits 6;
    type Coordinate_Type is record
        Lat : Float_Type;
        Lon : Float_Type;
        Alt : Float_Type;
    end record;
    
    type Status_Type is (Idle, Flying, Emergency, Landing);
end Types;
