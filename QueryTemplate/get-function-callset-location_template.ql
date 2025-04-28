/**
 * @name Find Function callset Location
 * @description Find All Function callset Location in the codebase
 * @id cpp/find-function-callset
 */

import cpp

from FunctionCall fc
where fc.getTarget().getName() = "buffer_copy_string_len_lc"
select 
"Function " + fc.getTarget().getName() + 
" is called at " + fc.getLocation().getFile() + 
":" + fc.getLocation().getStartLine().toString()