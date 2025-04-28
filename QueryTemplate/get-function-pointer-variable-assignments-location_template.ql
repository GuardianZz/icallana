/**
 * @name Find Function Pointer Variable Assignment Location
 * @description Find function pointer variable assignments in the codebase
 * @id cpp/find-fp-variable-assignment-location
 */


import cpp

from Variable v, AssignExpr assign
where v.getName() = "{fountion_pointer_variable}" and
      assign.getLValue() instanceof VariableAccess and
      assign.getLValue().(VariableAccess).getTarget() = v
select 
      "Function pointer variable " + v.getName() + 
      " is assigned at " + assign.getLocation().getFile() + 
      ":" + assign.getLocation().getStartLine().toString()