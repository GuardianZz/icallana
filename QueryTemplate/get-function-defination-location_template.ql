/**
 * @name Find Funtion Definition Location
 * @description Finds target funtion definition in the codebase
 * @id cpp/find-funtion-location
 */


import cpp

from Function f
where f.getName() = "{function_name}"
select 
    "Function " + f.getName() + " is defined in " + 
    f.getLocation().getFile() +
    " from line " + f.getLocation().getStartLine().toString() + 
    " to line " + f.getBlock().getLocation().getEndLine().toString()