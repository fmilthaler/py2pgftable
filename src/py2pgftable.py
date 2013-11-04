#File: py2pgftable.py
#Copyright (C) 2013 Frank Milthaler.
#
#This file is part of Py2PGFTable.
#
#Py2PGFTable is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Py2PGFTable is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Py2PGFTable. If not, see <http://www.gnu.org/licenses/>.
#
##This project aims to ease and automate the process, thus to fill 
##the gap between generating data and writing the corresponding 
##LaTeX commands to create a table.


import os
import commands
from io_routines import convert_filename_to_path_and_filename, sorted_nicely
import numpy as np



class Py2pgfplots:
  """
     An object to set parameters and write LaTeX code of a pgfplotstable
  """

  def __init__(self):
  # the constructor
  # initializing the dictionary holding the parameters:
  self.params = {}


  # Write array to a file, to use for pgfplots:
  def write_pgfplots_data_file(self, filename, array, array_labels=[]):
    """
       writes the elements of array into a file. If array_labels
       is passed, the first row of the datafile will have names
       for the columns.
    """
    # First, remove underscore sign from strings, as those give LaTeX problems in words,
    # plus preserve the LaTeX math mode:
    array_labels = remove_underscore_preserve_math_mode(', '.join(array_labels).strip(), replace_char='_')
    array_labels = array_labels.split(', ')
    # The same for the data stored in 'array', as this could be strings for tables:
    for i in range(len(array)):
      if (type(array).__name__=='ndarray'):
        # For numpy arrays, do this:
        tmp = str(list(array[i])).replace('[','').replace(']','')
      else:
        # For normal lists:
        tmp = ', '.join(array[i])
      tmp = remove_underscore_preserve_math_mode(tmp, replace_char='_')
      tmp = tmp.split(', ')
      for j in range(len(tmp)):
        array[i][j] = tmp[j]
    # Successfully removed underscore signs and preserved LaTeX math mode from header and data!
    # Continue:
    if (array_labels and (len(array[0]) != len(array_labels))):
      print "#################################################"
      print "# Length of array and array_labels are unequal! #"
      print "#################################################"
    # Write to file:
    datafile = open(filename, "w")
    # If array labels are given, write header:
    if (array_labels):
      for i in range(len(array_labels)):
        datafile.write(array_labels[i])
        if (i < len(array_labels)-1):
          datafile.write('\t')
        else:
          datafile.write('\n')
    # Assumption that all columns of array are of same length!
    rows = len(array)
    cols = len(array[0])
    # Write data to file:
    for i in range(rows):
      for j in range(cols):
        datafile.write(str(array[i][j]))
        datafile.write('\t') #seperation by tabular character
      datafile.write('\n') #newline after all columns in array are written
    datafile.closed



  # Write x and y coordinates to a file, to use for pgfplots:
  def write_pgfplots_data_file_simple(filename, x, y, array_labels=[]):
    """
       writes the elements of two input arrays
       (both assumed to be 1-dimensional)
       into the file 'filename'
    """
    if (array_labels and (len(array_labels) != 2)):
      print "#####################################"
      print "# Length of array_labels must be 2! #"
      print "#####################################"
    # Write to file:
    datafile = open(filename, "w")
    # If array labels are given, write header:
    if (array_labels):
      for i in range(len(array_labels)):
        datafile.write(array_labels[i])
        if (i < len(array_labels)-1):
          datafile.write('\t')
        else:
          datafile.write('\n')
    # Assumption that columns of x and y are of same length!
    for i in range(len(x)):
      datafile.write(str(x[i]))
      datafile.write('\t')
      datafile.write(str(y[i]))
      datafile.write('\n')
    datafile.closed


  # Writes header of pgfplots data file, that will be extended through 
  # append_pgfplots_data_file_simple(filename, array)
  def write_pgfplots_data_file_header_simple(filename, array_labels):
    """
       writes the header information of a pgfplots datafile
       that can be extended through 
       append_pgfplots_data_file_simple(filename, array)
    """
    # Write to file:
    datafile = open(filename, "w")
    # If array labels are given, write header:
    for i in range(len(array_labels)):
      datafile.write(array_labels[i])
      if (i < len(array_labels)-1):
        datafile.write('\t')
      else:
        datafile.write('\n')
    datafile.closed


  # Appends one-dimensional array as a row to a datafile:
  def append_pgfplots_data_file_simple(filename, array):
    """
       appends the 1-dimensional array 'array'
       to the datafile 'filename'.
    """
    # Write to file:
    datafile = open(filename, "a")
    for i in range(len(array)):
      datafile.write(array[i])
      if (i < len(array)-1):
        datafile.write('\t')
      else:
        datafile.write('\n')
    datafile.closed


  # Appends a single column to a pgfdat file, including the header
  def append_column_pgfplots_data_file_simple(filename, col):
    """
       appends a column of data including a header
       describing what kind of data the column
       holds to the file 'filename'. The given
       array 'col' must contain the same number of 
       elements as the existing file 'filename'
       has rows.
    """
    # Open filename for reading and get all lines:
    file = open(filename, 'r')
    alllines = file.readlines()
    file.close()
    # Checking the consistency of number of rows in filename
    # with number of elements in col:
    if (len(alllines) != len(col)):
      printc("The given column has an insufficient number of elements compared to the data in "+filename+" and hence cannot be added to the file.", "red", False); print
    else:
      # Assemble new lines, including the new column:
      z = 0
      newlines = []
      #for line in file:
      for line in alllines:
          newlines.append(line.strip()+'\t'+str(col[z])+'\n')
          z = z+1
      # Now write the assembled lines with new column to the file on the disk:
      file = open(filename, 'w')
      for newline in newlines:
        file.write(newline)
      file.close()


  def read_column_pgfplots_data_file(filename, colname):
    """ This method reads in the data of a specific column in a csv/pgfplots datafile.
        The datafile must have column names in the first line, with the corresponding 
        data in the lines below.
        Input:
          filename: String of the filename of the datafile to read data from
          colname: String of the corresponding column name we want the data from
        Output:
          data: List of values from the datafile
          status: Integer determining the status:
            0: no error
            1: column with given colnames was not found
            2: error occured during the reading in of data
    """
    status = 0
    datafile = open(filename, 'r')
    # Check the first line for the column names, to find out which columns we have to extract:
    colindex = -1
    colnames = datafile.readline().strip()
    # Get a first guess of what seperation character is used in that datafile:
    if ('\t' in colnames): sepchar = '\t'
    elif (';' in colnames): sepchar = ';'
    elif (',' in colnames): sepchar = ','
    elif (' ' in colnames): sepchar = ' '
    # Splitting the line where sepchar appears:
    colnames = colnames.split(sepchar)
    for i in range(len(colnames)):
      if (colnames[i] == colname):
        colindex = i
    if (colindex < 0):
      status = 1
      print "--------------------------------------------------------------------------------------------"
      print "Error: column with label \""+colname+"\" could not be found in the header of file "+filename+"."
    # Now read in the data and store it in arrays:
    if (status == 0):
      data = []
      for line in datafile:
        if (len(line.strip()) > 0):
          try:
            line = line.strip().split(sepchar)
            data.append(float(line[colindex]))
          except:
            print "--------------------------------------------------------------------------------------------"
            print "Error, could not convert data in file "+filename+" into a floating point number!"
            print "Number was: "+line[colindex]+"."
            status = 2
            break
    # Done processing the datafile, so close it:
    datafile.close()
    return data, status


  def remove_underscore_preserve_math_mode(string, replace_char='_'):
    """Checks if string contains underscore signs outside math mode and replaces those"""
    if (replace_char == ''):
      replace_char == ' '
    num_dollar = string.count('$')
    num_undscr = string.count('_')
    ind_dollar = []
    modstring = ''
    if (num_undscr != 0):
      if (num_dollar != 0):
        index = string.find('$')
        for z in range(num_dollar):
          ind_dollar.append(index)
          index = string.find('$', index+1)
        tmp = (string[0:ind_dollar[0]].replace('_',replace_char)) #starting point
        modstring = modstring+tmp
        for i in range(len(ind_dollar)):
          if (i%2 == 0): #beginning of mathmode found --> skip substring
            tmp = (string[ind_dollar[i]:ind_dollar[i+1]+1])
            modstring = modstring+tmp # this is the mathmode string
          else:  # append underscore-free string outside mathmode
            if (i != len(ind_dollar)-1):
              tmp = (string[ind_dollar[i]+1:ind_dollar[i+1]].replace('_',replace_char))
            else:
              tmp = (string[ind_dollar[i]+1:].replace('_',replace_char))
            modstring = modstring+tmp
      else:
        # No mathmode found, just replace underscores with spaces:
        modstring = string.replace('_', replace_char)
    else: # No underscore sign found:
      modstring = string
    return modstring


  ##########################
  # PGFPlotsTable Methods: #
  ##########################

  def write_pgfplotstable_tex_file(texfile, datafile, datacolnames, data, printcols=None, printcolnames=None, precision=None, string_replace=None, postprocessing=None, caption=None):
    """ This method generates a tex file for a pgfplotstable, whereas
        the content and description/header is given in a file, which
        filename is given by an input argument.
        Input:
         texfile: Name of the texfile to be written to.
         datafile: Name of the pgfdatafile in which the table's content
           is stored.
         datacolnames: List of column names/header in the datafile
         data: 2D list, that contains the data to be printed, this is only
           used in order to work out the type of the element, such that
           we can automatically set the pgfplotstable setting for that column
         printcols: List of columns to print in the table, whereas the elements
           of 'printcols' refer to the strings of the column labels of the datafile
         printcolnames: 1D dictionary of column labels as they appear in the
           datafile, and their values being the string that should be printed instead.
         precision: 2D List of two elements, first is a string of the corresponding column
           name, second is a string of column data type and numerical precision entries
         string_replace: List of lists, with the inner list having n elements,
           with the first element being the string of the the affected columnname,
           and the following elements being lists of two elements each, with the
           first element of those list being the text to be replaced, and the
           second the text that should appear in the table instead.
           Example: [
                     ['col1', ['replace', 'write-this'], ['replace_this_too', 'this-instead']],
                     ['col2', ['replace-here', 'this-is-good']],
                     ...
                    ]
         postprocessing: List of lists, whereas inner list has 4 elements:
           1: column name to postprocess, 2: LaTeX code to add to the column,
           3: must either be 'unit' or 'trailing' and 4: is either True or False, determining
           if the second element is supposed to be a unit or not.
         caption: String of the caption to be printed below the table.
    """
    # First of all, examine texfile and datafile strings, and find relative paths of them:
    (texfile_path, texfile) = convert_filename_to_path_and_filename(texfile)
    (datafile_path, datafile) = convert_filename_to_path_and_filename(datafile)
    # Check if path of datafile is same path as texfile:
    if (datafile_path.find(texfile_path) == 0):
      if (len(datafile_path) == len(texfile_path)):
        # If so, datafile_path must be '.', as LaTeX will search from it's path:
        datafile_path = '.'
      else:
        # Subtract texfile_path from datafile_path:
        datafile_path = datafile_path[len(texfile_path):]
    # pgftable_name is the name that will refer to the data of the table
    # in LaTeX/PGF:
    pgftable_name = 'pgftable' + texfile[:-4]
    # Get rid of digits in pgftable_name, as digits are not allowed in LaTeX variable names:
    pgftable_name = pgftable_name.replace('0','').replace('1','').replace('2','').replace('3','').replace('4','').replace('5','').replace('6','').replace('7','').replace('8','').replace('9','').replace('_','').replace('-','')

    # Now start writing files:
    file = open(texfile_path+'/'+texfile, "w")
    print>>file, "%% Generated file to generate a table data from a pgfdatafile using pgfplotstable"
    print>>file, ""
    print>>file, "\\documentclass[11pt]{article}"
    print>>file, "% Set page legths"
    print>>file, "\\special{papersize=550cm,550cm}"
    print>>file, "\\hoffset-0.8in"
    print>>file, "\\voffset-0.8in"
    print>>file, "\\setlength{\\paperwidth}{550cm}"
    print>>file, "\\setlength{\\paperheight}{550cm}"
    print>>file, "\\setlength{\\textwidth}{545cm}"
    print>>file, "\\setlength{\\textheight}{545cm}"
    print>>file, "\\topskip0cm"
    print>>file, "\\setlength{\\headheight}{0cm}"
    print>>file, "\\setlength{\\headsep}{0cm}"
    print>>file, "\\setlength{\\topmargin}{0cm}"
    print>>file, "\\setlength{\\oddsidemargin}{0cm}"
    print>>file, "% set the pagestyle to empty (removing pagenumber etc)"
    print>>file, "\\pagestyle{empty}"
    print>>file, ""
    print>>file, "% Additional packages:"
    print>>file, "\\usepackage{amssymb}"
    print>>file, "\\usepackage{textcomp}"
    print>>file, "\\usepackage{units}"
    print>>file, "\\usepackage[english]{babel}"
    print>>file, "\\usepackage[babel]{csquotes}"
    print>>file, "\\usepackage{color}"
    print>>file, "\\usepackage{pdflscape}"
    print>>file, ""
    print>>file, "% PGF:"
    print>>file, "\\usepackage{tikz}"
    print>>file, "% \\usepackage{pgfplots}"
    print>>file, "\\usepackage{pgfplotstable}"
    print>>file, "% recommended:"
    print>>file, "\\usepackage{booktabs}"
    print>>file, "\\usepackage{array}"
    print>>file, "\\usepackage{colortbl}"
    print>>file, ""
    print>>file, "\\begin{document}"
    print>>file, ""
    print>>file, "\\begin{landscape}"
    print>>file, ""
    print>>file, "% Load table settings:"
    print>>file, "\\input{pgftablesettings_"+texfile+"}"
    print>>file, "% Load table data:"
    print>>file, "\\pgfplotstableread{"+datafile_path+"/"+datafile+"}\\"+pgftable_name
    print>>file, ""
    if (not (caption is None)): # Caption given, so print caption, and create table environment
      print>>file, "\\begin{table}"
    else:
      None # Just create the table, without table environment, and without caption and label, that should be done in the 
    print>>file, "  \\centering"
    # Make a string, seperated by commas, of the given list 'printcols'
    # First, remove underscore signs from printcols:
    # Remove underscore signs from datacolnames:
    if (not (printcols is None)):
      printcols = remove_underscore_preserve_math_mode(','.join(printcols).strip(), replace_char='_')
    else:
      printcols = remove_underscore_preserve_math_mode(','.join(datacolnames).strip(), replace_char='_')
    print>>file, "  \\pgfplotstabletypeset[columns={"+printcols+"},"
    print>>file, "  ]\\"+pgftable_name
    # Add caption and label:
    if (not (caption is None)):
      print>>file, "  \\caption{"+caption+"}"
      print>>file, "  \\label{tab:"+texfile[:-4]+"}"
    # End of table environment:
    if (not (caption is None)):
      print>>file, "\\end{table}"
    print>>file, ""
    print>>file, "\\end{landscape}"
    print>>file, ""
    print>>file, "\\end{document}"
    # Close texfile:
    file.closed

    # Now write the pgftable settings file:

    file = open(texfile_path+"/pgftablesettings_"+texfile, "w")
    print>>file, "% PGFPlotsTable settings are defined below."
    print>>file, "% To load them:"
    print>>file, "% \\input{"+texfile_path+"/pgftablesettings_"+texfile+"}"
    print>>file, ""
    print>>file, "\\pgfplotstableset{"
    print>>file, "    %    col sep=&,row sep=\\\\"
    print>>file, "    %    col sep=space, ignore chars={(,),\ ,\#}"
    print>>file, "    % Coloring:"
    print>>file, "    every even row/.style={before row={\\rowcolor[gray]{0.85}}}," # \\rowcolor[blue]{0.5}
    print>>file, "    % Table header:"
    print>>file, "    every head row/.style={before row=\\toprule,after row=\midrule},"
    print>>file, "    every last row/.style={after row=\\bottomrule},"
    print>>file, "    % Set column parameters:"
    # Remove underscore signs from datacolnames:
    datacolnames = remove_underscore_preserve_math_mode(', '.join(datacolnames).strip(), replace_char='_')
    datacolnames = datacolnames.split(', ')
    # Now define the column names/strings, as they should appear in the document:
    colprintnames = remove_underscore_preserve_math_mode(', '.join(datacolnames).strip(), replace_char='\_')
    colprintnames = colprintnames.split(', ')
    print>>file, "    columns={"+', '.join(datacolnames)+"},"
    # Depending on the type of element in 
    for j in range(len(datacolnames)):
      string = False
      # Set entry for current column, and define column name:
      # First, find out if datacolnames[j] is found in printcolnames, if so, the name of the column was set to change:
      if (not (printcolnames is None) and datacolnames[j] in printcolnames):
        printcolname = printcolnames[datacolnames[j]]
        # remove unwanted characters from that string:
        printcolname = remove_underscore_preserve_math_mode(printcolname.strip(), replace_char='\_')
      else:
        printcolname = colprintnames[j]
      print>>file, "    columns/"+datacolnames[j]+"/.style={column name="+printcolname+","
      # Finding out if the data of this column is a number, or a string:
      # First, check if a precision was specified for this column:
      precision_entry_found = False
      if (not (precision is None)):
        for i in range(len(precision)):
          if (datacolnames[j] == precision[i][0]):
            # Then print that entry:
            print>>file, "        "+precision[i][1]+","
            precision_entry_found = True
            # And break out of the loop:
            break
      if (not precision_entry_found):
        try:
          tmp = float(data[0][j])
          # For this particular case, we want strings only, although most entries are actually numbers:
          #raise Exception # raising an exception will force the entry to be treated as a string!
          # If we were able to convert, then tell pgfplotstable to use format numbers:
          # Now find out if it is an integer or float:
          # First of all, if the current column name is in string_replace, raise an exception:
          for i in string_replace:
            if (any([datacolnames[j] in string_replace_item for string_replace_item in string_replace])):
              raise Exception
          # If no entry of this column is in string_replace or precision, continue to convert the string into a number:
          try:
            tmp = int(data[0][j])
            # This is an integer:
            print>>file, "        sci,"
            print>>file, "        precision=0, fixed,"
          except:
            # This is a floating point number:
            print>>file, "        sci, sci zerofill,"
            print>>file, "        precision=3, fixed,"
          if (not (postprocessing is None)):
            # Check if postprocessing is done later for this column, 
            # and if so, do not align numbers by decimal point
            if (not (any([datacolnames[j] in postitem for postitem in postprocessing]))):
              print>>file, "        dec sep align,"
            else: #do not align by decimal point
              print>>file, "        %dec sep align,"
          else: # If postprocessing is None (not given by user, use dec sep align:
              print>>file, "        dec sep align,"
        except:
          string = True
          # If that failed, it is a string:
          print>>file, "        string type,"
          # Now, if present, write string replace information to the texfile:
          boolean = False
          if (not (string_replace is None)):
            for item in string_replace:
              if (item[0] == datacolnames[j]): # item[0] is the column name
                for replace in item[1:]: # in replace are the replacement strings
                  print>>file, "        string replace={"+str(replace[0])+"}{"+str(replace[1])+"},"
                  # Check if there is an entry of a boolean, because booleans should be
                  # centered, whereas strings should be left aligned
                  if (replace[0] == 'True' or replace[0] == 'False'):
                    boolean = True
      # If this is the first column, add a vertical line in the table:
      if (j==0):
        print>>file, "        column type={l|},"
      else:
        if (string and not boolean):
          print>>file, "        column type=r," #lets assume, we want the strings to be right aligned
        elif (string and boolean):
          print>>file, "        column type=c,"
      # Add postprocessing entries (for now only units possible):
      if (not (postprocessing is None)):
        for item in postprocessing:
          if (item[0] == datacolnames[j]):
            if (item[2] != 'code'):
              print>>file, "        postproc cell content/.append style={"
              if (item[2] == 'unit' and item[3] == True):
                print>>file, "            /pgfplots/table/@cell content/.add={$\unit[}{]{"+item[1]+"}$},"
              elif (item[2] !='unit' and item[2] !='trailing' or item[3] == False) :
                print>>file, "            /pgfplots/table/@cell content/.add={"+item[1]+"}{},"
              elif (item[2] =='trailing' and item[3] == True):
                print>>file, "            /pgfplots/table/@cell content/.add={}{"+item[1]+"},"
            elif (item[2] =='code' and item[3] == True):
              # This inner list append pgf code to the postprocessing in pgf, thus this list has six element
              print>>file, "            postproc cell content/.append code={"
              print>>file, "                \ifnum\pgfplotstablerow="+str(item[1])
              print>>file, "                    \pgfkeysalso{/pgfplots/table/@cell content/.add={}{"+str(item[4])+"}}"
              print>>file, "                \else"
              print>>file, "                    \pgfkeysalso{/pgfplots/table/@cell content/.add={}{"+str(item[5])+"}}"
              print>>file, "                \\fi"
            print>>file, "        },"
      print>>file, "    },"
    print>>file, "}"
    file.closed
    # Now that the (standalone) file has been written, write another file that can be included
    # in another latex document with \input{..}
    # First read in the file that was just written to disk:
    infile = open(texfile_path+'/'+texfile, 'r')
    outfile = open(texfile_path+'/'+texfile.replace('.tex','')+'_include.tex', 'w')
    write_to_file = False
    for line in infile:
      if ('% Load table settings' in line):
        write_to_file = True
        outfile.write('% Load this file in your LaTeX document with:\n')
        outfile.write('% \input{'+texfile.replace('.tex','')+'_include.tex'+'}\n\n')
      elif (not (caption is None) and '\end{table}' in line): # \end{table} is only part of the output if caption was given!
        write_to_file = False
        outfile.write(line)
      elif (caption is None and '\end{landscape}' in line):
        write_to_file = False
      if (write_to_file):
        outfile.write(line)
    outfile.close()  
    infile.close()


  def prevent_dimension_too_large_error(dir, texfilename):
    """ This method is executed if the string '! Dimension too large'
        was found in pdflatex's output. It tries to make minor modifications
        to the given tex file in order to prevent this error from happening.
        Input:
         dir: Directory name where the tex file is in
         texfilename: Name of the tex file to run
    """
    # Dictionary to store relevant data for each datafile we find in texfilename:
    datadict = {}
    # First, let's find out the relevant datafiles we have to check:
    # Open texfile:
    texfile = open(dir+'/'+texfilename, 'r')
    texfile_lines = texfile.readlines()
    texfile.close()
    # Assemble a list of addplot commands in the texfile, those are the lines
    # we have to process:
    curve_cmds = []
    for line in texfile_lines:
      if (line.strip().startswith('\\addplot')):
        curve_cmds.append(line.strip())
    for line in curve_cmds:
      # Get the datafilename:
      datafilename = line.split('{')[-1].split('}')[0]
      # And get the relevant columns of that datafile:
      colnames = line.split('table[')[-1].split(']')[0]
      colnames = colnames.split(',')
      for col in colnames:
          col = col.replace(' ','')
          if ('x=' in col):
            xcolname = col.split('=')[-1].strip()
          elif ('y=' in col):
            ycolname = col.split('=')[-1].strip()
      # Now add column labels into datadict:
      datadict.update({datafilename : {'xcolname' : xcolname, 'ycolname' : ycolname}})

    # Now scan the data of relevant columns to find min/max x/y values of each plot in texfilename
    for datafilename in sorted(datadict.iterkeys()):
      # Open datafile:
      # Now get the corresponding column names:
      xcolname = datadict[datafilename]['xcolname']
      ycolname = datadict[datafilename]['ycolname']
      # Potential error message for reading in data from the datafile:
      datafile_errmsg = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
      datafile_errmsg = datafile_errmsg+"\nSerious error was found. Please check your datafile"
      datafile_errmsg = datafile_errmsg+"\n   \""+datafilename+"\""
      datafile_errmsg = datafile_errmsg+"\nfor valid floating point numbers and"
      datafile_errmsg = datafile_errmsg+"\nthat the column labels are as they are supposed to be."
      datafile_errmsg = datafile_errmsg+"\nSkipping this datafile!"
      # Now read data from datafile:
      (xdata, status) = read_column_pgfplots_data_file(datafilename, xcolname)
      if (status != 0):
        # Error occured, so skip this datafile
        print datafile_errmsg
        continue
      (ydata, status) = read_column_pgfplots_data_file(datafilename, ycolname)
      if (status != 0):
        # Error occured, so skip this datafile
        print datafile_errmsg
        continue
      # Now find the min/max values:
      xmin = min(xdata); xmax = max(xdata)
      ymin = min(ydata); ymax = max(ydata)
      # Now that we have the min/max values of the relevant datacolumns in datafile, 
      # store those min/max values in the dict:
      datadict[datafilename].update({'xmin':xmin, 'xmax':xmax, 'ymin':ymin, 'ymax':ymax})

    # Now that we have all the data we need, lets modify the texfile with the pgfplot commands slightly
    # in order to prevent the '! dimension too large error':
    xmin = 10e15; xmax = -10e15; ymin = 10e15; ymax = -10e15
    for datafilename in sorted(datadict.iterkeys()):
      print "datafilename = ", datafilename
      # Now determine the xmin/xmax and ymin/ymax values of the entire plot:
      if (datadict[datafilename]['xmin'] < xmin): xmin = datadict[datafilename]['xmin']
      if (datadict[datafilename]['xmax'] > xmax): xmax = datadict[datafilename]['xmax']
      if (datadict[datafilename]['ymin'] < ymin): ymin = datadict[datafilename]['ymin']
      if (datadict[datafilename]['ymax'] > ymax): ymax = datadict[datafilename]['ymax']
    # The lines of the texfile are still stored in the variable 'texfile_lines'
    new_texfile_lines = []
    for line in texfile_lines:
      # Find line starting with 'scale only axis':
      if (line.strip().startswith('scale only axis')):
        # Commenting out 'scale only axis command:
        new_texfile_lines.append(line.split('scale only axis')[0]+'% scale only axis'+line.split('scale only axis')[-1])
      elif (line.strip().startswith('restrict x to domain') or line.strip().replace(' ','').startswith('%restrictxtodomain')):
        precmndstring = line.split('restrict x to domain')[0].split('%')[0]
        new_texfile_lines.append(precmndstring+'restrict x to domain='+str(xmin)+':'+str(xmax)+', % use this if you get a \'dimension too large\' error\n')
      elif (line.strip().startswith('restrict y to domain') or line.strip().replace(' ','').startswith('%restrictytodomain')):
        precmndstring = line.split('restrict y to domain')[0].split('%')[0]
        new_texfile_lines.append(precmndstring+'restrict y to domain='+str(ymin)+':'+str(ymax)+', % use this if you get a \'dimension too large\' error\n')
      else:
        new_texfile_lines.append(line)
    # Now the new lines of the texfile have been assembled, write them to disk:
    texfile = open(texfilename, 'w')
    for new_line in new_texfile_lines:
      texfile.write(new_line)
    texfile.close()




  def write_dict_status_pgftable(directory, texfilename, dict, first_colname, printcols=None, printcolnames=None, precision=None, string_replace=None, postprocessing=None, caption=None, pdflatex=True, pdfcrop=True):
    """ This method assembles lists of the content of the given dictionary
        and then calls methods to write pgf data files of the dictionary,
        and to update the pdf showing the table.
        Input:
         directory: The directory in which the table should be written to
         texfilename: String of the filename of the pgf-tex-table.
         dict: 2D Dictionary of which all content will be written to file
         first_colname: String of the name of the first column, e.g. 'simulation name'
         printcols: List of columns to print in the table, whereas the elements
           of 'printcols' refer to the strings of the column labels of the datafile
         printcolnames: 1D dictionary of column labels as they appear in the
           datafile, and their values being the string that should be printed instead.
         precision: 2D List of two elements, first is a string of the corresponding column
           name, second is a string of column data type and numerical precision entries
         string_replace: List of lists, with the inner list having n elements,
           with the first element being the string of the the affected columnname,
           and the following elements being lists of two elements each, with the
           first element of those lists being the text to be replaced, and the
           second the text that should appear in the table instead.
           Example: [
                     ['col1', ['replace', 'write-this'], ['replace_this_too', 'this-instead']],
                     ['col2', ['replace-here', 'this-is-good']]
                    ]
         postprocessing: List of lists, whereas inner list has 4 elements:
           1: column name to postprocess, 2: LaTeX code to add to the column,
           3: must either be 'unit' or 'trailing' and 4: is either True or False, determining
           if the second element is supposed to be a unit or not.
         pdflatex: Boolean determining if pdflatex should run on the
           generated texfile
         pdfcrop: Boolean determining if pdfcrop should run on the
          generated pdf
    """
    # First assemble the header of the table:
    for dir in sorted_nicely(dict.iterkeys()):
      datadict = dict[dir]
      array_labels = [first_colname]
      for key, value in datadict.items():
        # Key is pratically the header of our table, with a leading
        # 'dirname', as the directory name of the simulation is not
        # stored in 'key', but in 'dir'. value is the content of the
        # table.
        array_labels.append(key)
      break
    # Now the content of the table, each row below the header:
    if (string_replace is None):
      string_replace = []
    table_rows = [[0 for j in range(len(array_labels))] for i in range(len(dict.keys()))]
    i = 0
    for dir in sorted_nicely(dict.iterkeys()):
      datadict = dict[dir]
      j = 0
      table_rows[i][j] = str(dir)
      for key, value in datadict.items():
        j = j + 1
        table_rows[i][j] = str(value)
      # For this dirname, add an entry into string_replace,
      # in order to add color and proper \_ for the table:
      string_replace.append([first_colname, [dir, remove_underscore_preserve_math_mode(dir, replace_char='\_')]])
      i = i + 1

    # Write datafile:
    pgfdat_filename = directory+'/'+texfilename.split('.tex')[0].split('/')[-1]+'_data.pgfdat'
    write_pgfplots_data_file(pgfdat_filename, table_rows, array_labels=array_labels)
    # Now write texfile to generate the pdf with the table:
    texfile = directory+'/'+texfilename

    # If this method was given a specific header, meaning a specific order of printing the columns
    # in the table, then this list should be given to the texfile, rather than the unsorted columnlist
    # that was obtained from the dictionary.
    if (printcols is None):
      printcols = array_labels

    # Write to texfile:
    write_pgfplotstable_tex_file(texfile, pgfdat_filename, array_labels, table_rows, printcols=printcols, printcolnames=printcolnames, precision=precision, string_replace=string_replace, postprocessing=postprocessing, caption=caption)
    if (pdflatex):
      # Produce pdf:
      (dir, texfile) = convert_filename_to_path_and_filename(texfile)
      run_latex(dir, texfile)
      if (pdfcrop):
        # Crop white space from pdf:
        run_pdfcrop(dir, texfile[:-3]+'pdf', texfile[:-3]+'pdf')




  def run_latex(dir, filename):
    """ This method runs pdflatex on the given filename
        in directory dir and if successful produces a pdf
        Input:
         dir: Directory name where the tex file is in
         filename: Name of the tex file to run
    """
    cmd = 'cd '+dir+'; pdflatex -interaction=nonstopmode '+filename
    shellout = commands.getoutput(cmd)
    # For testing only:
    # Printing out shellout:
    if ('! Dimension too large.' in shellout):
      print "=============================================================="
      #print "Dimension too large error found in pdflatex output. Making a few"
      #print "adjustments on the given tex file to prevent this error."
      #print "filename: ", filename
      prevent_dimension_too_large_error(dir, filename)
      #for line in shellout:
      #  print "line: ", line
      #  print "shellout: "
      #  print shellout
      print "=============================================================="
    # Check we have to rerun, because of labels:
    if (shellout.find('LaTeX Warning: Label(s) may have changed.') >= 0):
      shellout = commands.getoutput(cmd)


  def run_pdfcrop(dir, filename, newfilename):
    """
        Runs pdfcrop on a pdf, in order to remove white space
        Input:
         dir: String of the directory where the pdf is in
         filename: String of the pdf filename
         newfilename: String of the cropped version of 'filename'
    """
    cmd = 'cd '+dir+'; pdfcrop '+filename+' '+newfilename
    shellout = commands.getoutput(cmd)
