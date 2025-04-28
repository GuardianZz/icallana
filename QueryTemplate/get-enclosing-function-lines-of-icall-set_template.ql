/**
 * @name Find Function boundaries for target call site
 * @description Find function boundaries for target call site in the codebase
 * @kind table
 * @id cpp/find-function-boundaries
 */

import cpp

from ExprCall fc, Function f
where
fc.getLocation().getFile().getBaseName() = "{file_name}" and
fc.getLocation().getStartLine() = {line_number} and
f = fc.getEnclosingFunction()
select "File Path: " + f.getLocation().getFile(),
    "Start Location: Line " + f.getLocation().getStartLine(),
    "End Location: Line " + f.getBlock().getLocation().getEndLine()