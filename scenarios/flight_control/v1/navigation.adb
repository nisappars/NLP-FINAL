with Types; use Types;
with Utils;
package Navigation is
    procedure Calculate_Route(Start, Dest : Coordinate_Type; Time : out Float_Type);
end Navigation;

package body Navigation is
    procedure Calculate_Route(Start, Dest : Coordinate_Type; Time : out Float_Type) is
        D : Float_Type;
    begin
        D := Utils.Dist(Start, Dest);
        Time := D / 500.0; -- Assume 500 speed
    end Calculate_Route;
end Navigation;
