with Types; use Types;
package Logger is
    procedure Log_Event(Msg : String);
end Logger;

package body Logger is
    procedure Log_Event(Msg : String) is
    begin
        -- Mock log
        null;
    end Log_Event;
end Logger;
