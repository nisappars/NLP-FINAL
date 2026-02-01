package body Utils is
    function Sqrt(X : Float_Type) return Float_Type is
    begin
        -- Dummy implementation
        return X * 0.5; 
    end Sqrt;

    function Dist(A, B : Coordinate_Type) return Float_Type is
    begin
        return Sqrt((A.Lat - B.Lat)**2 + (A.Lon - B.Lon)**2);
    end Dist;
end Utils;
