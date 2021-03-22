CSC 454 Assignment 4

Team Members:
Jinhao Zhang, jzh160@ur.rochester.edu
Mohammed Ibrahim Khan, mkhan26@ur.rochester.edu

Language Used: Python

Instructions to run:
- Keep all rust files in the same directory as the 'xref.py' file.
- Build/compile the rust file with the main function using the following command:
	rustc -g <main-file>.rs
- Now, run xref.py providing built rust executable name as command line argument:
	python xref.py <main-file>  (omit the extension '.rs' since its an object code)
- View the generated 'xref.html' in a browser.
- The two llvm dumps (dwarf and object dumps) will be written in files 'dwarfdump.txt' and 'objdump.txt'.

The main code file is 'xref.py'

Description of the task:
We are given a rust code and we read the output provided by dwarfdump on the given code. We extract key information about variables used such as their name and scope. We also gather information about functions defined and used. We gather this information by using regular expressions (re in python). Then we match collected information with lines in various files of the source code and display it in an HTML document.