    File: README.md
    Copyright (C) 2013 Frank Milthaler.

    This file is part of Py2PGFTable.

    Py2PGFTable is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    Py2PGFTable is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with Py2PGFTable. If not, see <http://www.gnu.org/licenses/>.


Py2PGFTable
================

TeX/LaTeX (see http://www.latex-project.org/) has been used as a configurable, clean, robust and free typesetting system for many decades now. Via many contributions from its community it has seen many extensions and enhancements via packages that can easily used (see http://www.ctan.org). Despite many packages for generating tables in LaTeX, it still remains cumbersome task to do.

This project aims to ease and automate the process, thus to fill the gap between generating data and writing the corresponding LaTeX commands to create a table.

As the comprehensive package pgfplotstable (see http://pgfplots.sourceforge.net/) provides many useful features to create tables in LaTeX, this code writes a LaTeX file to disk which uses pgfplotstable. The file can then be included in your LaTeX document with the \input{filename} command.

Note
================
This is still in the alpha stage, documentation and examples will be available once it is moved to beta.

Dependencies
================
 * Python (>= v. 2.7, see http://python.org)
 * PGFPlotsTable (to be on the safe side, >= v. 1.9, see http://ctan.org/pkg/pgfplotstable and http://pgfplots.sourceforge.net/)
