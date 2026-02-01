with Types; use Types;
with Utils;
package Navigation is
    -- CHANGED: Added Wind_Factor parameter
    procedure Calculate_Route(Start, Dest : Coordinate_Type; Wind_Factor : Float_Type; Time : out Float_Type);
end Navigation;

package body Navigation is
    procedure Calculate_Route(Start, Dest : Coordinate_Type; Wind_Factor : Float_Type; Time : out Float_Type) is
        D : Float_Type;
    begin
        D := Utils.Dist(Start, Dest);
        -- CHANGED: Logic accounts for wind
        Time := (D / 500.0) * Wind_Factor;
    end Calculate_Route;
end Navigation;
