/**
 * @name Find macro defination location
 * @description Finds target macro definitions in the codebase
 * @id cpp/find-macro-location
 */

import cpp

from Macro m
where m.getName() = "{macro_name}"
select 
    "Macro " + m.getName() + " is defined at " +
    m.getLocation().getFile() + ":" +
    m.getLocation().getStartLine().toString()