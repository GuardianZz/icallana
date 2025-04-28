/**
 * @name Find function pointer Definition Location
 * @description Finds function pointer definitions in the codebase
 * @id cpp/find-function-pointer-location
 */

import cpp

from Variable v, VariableDeclarationEntry decl
where v.getName() = "{function_point_name}" and
      decl.getVariable() = v and
      decl.isDefinition()
select 
"Function pointer " + v.getName() + 
" is defined at " + decl.getLocation().getFile() + 
":" + decl.getLocation().getStartLine().toString()