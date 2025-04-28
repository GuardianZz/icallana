/**
 * @name Find struct pointer field Assignment Locations
 * @description Finds struct pointer field Assignment Locations in the codebase
 * @id cpp/find-sp-field-assignment-location
 */

import cpp

from AssignExpr assign, PointerFieldAccess pfa
where
  assign.getLValue() = pfa 
  and pfa.getTarget().getName() =  "{field_name}"
  and pfa.getQualifier().getType().getName() = "{struct_name *}"
select 
  "Field " + pfa.getTarget().getName() + " of struct pointer " + 
  pfa.getQualifier().getType().getName() + 
  " is assigned at " + assign.getLocation().getFile() + 
  ":" + assign.getLocation().getStartLine().toString()