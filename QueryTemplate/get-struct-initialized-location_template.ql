/**
 * @name Find struct initialized Location
 * @description Find struct initialized Location in the codebase
 * @id cpp/find-struct-initialized
 */

import cpp

from Variable v, Initializer i
where v.getName() = "{struct_name}"
and v.getType().getUnspecifiedType().hasSpecifier("{struct_type}")
and i.getDeclaration() = v
select 
    "Struct " + v.getName() + " is initialized in " + 
    i.getLocation().getFile() +
    " from line " + i.getLocation().getStartLine().toString() + 
    " to line " + i.getLocation().getEndLine().toString()