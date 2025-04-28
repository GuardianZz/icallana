/**
 * @name Find Struct Definition Location
 * @description Finds target struct definitions in the codebase
 * @id cpp/find-struct-location
 */

import cpp

from Struct s, TypedefType t
where s.getName() = "{struct_name}"
and t.getName() = "{struct_name}"
select  
"Struct " + s.getName() + " is defined at " + s.getLocation().getFile() +
" from line " + s.getLocation().getStartLine().toString() + 
" to line " + t.getLocation().getEndLine().toString()