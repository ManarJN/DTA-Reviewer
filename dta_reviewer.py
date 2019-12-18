# -*- coding: utf-8 -*-
"""
Data Transfer Reviewer program:
    Checks that vendor transfer files adhere to Data Transfer Agreement.  Generates output.txt file with list of
    discrepancies per observation, and summary.txt file with list of discrepancies grouped by type of discrepancy.

Created on Tue May 21 12:23:56 2019
@author: manarnaboulsi

Before running program, fill out:
  - Setup section below
  - patterns.txt (tab-delimited) with regex conditions to check each variable against [Var Regex]
  - conditions.txt (tabl-delimited) with non-regex conditions to check variables against [Var Condition]
  - lbtests.txt (tab-delimited) with list of lab tests being performed [Labtype Labtest Saslabnm Lbmethod Tstcd Tstnam
                                                                        Item    Item    Item     Item     Item  Item]
  - vissched.txt with list of visits scheduled (tab-delimited) [Day Code]
"""

import csv
import os
import re
import sys
from collections import defaultdict
from tkinter import *
from tkinter import filedialog 
from tkinter import messagebox

# =============================================================================
# Setup
# =============================================================================
folder_dt = ''  # location of data transfer file
output_location = ''  # location output.txt and summary.txt generated files should be saved


# =============================================================================
# TKinter Setup
# =============================================================================

def tk_main():
    # app creation
    root = Tk()
    root.title("Vendor Data Transfer Review")
            
    # get height and width of screen to center window
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    
    position_right = int(root.winfo_screenwidth()/2 - window_width/2)
    position_down = int(root.winfo_screenheight()/2 - window_height/2)
    
    def exit_function():
        root.destroy()
        sys.exit()
        
    def doc_selection():
        root.doc_transfer = filedialog.askopenfilename(initialdir=output_location,
                                                       title="Data Transfer File")
        
        global doc_transfer
        doc_transfer = root.doc_transfer
        
        E1.delete(0, END)
        E1.insert(0, doc_transfer)
       
    def done():
        if not E1.get() and not E2.get():
            messagebox.showinfo("Error", "Please fill all boxes")
        else:
            if root.doc_transfer != "":
                global study, vendor, folder_vendor
                study = doc_transfer.split("/")[4]
                vendor = doc_transfer.split("/")[8]
                folder_vendor = os.path.join(folder_dt, study, vendor)
            
                if E1.get() is not "" and E2.get() is not "":
                    if not os.path.exists(folder_vendor):
                        messagebox.showinfo("Error", ("Study Vendor folder not found in filescan folder." +
                                                      "\nPlease ensure selected file is correct or create missing folder in filescan folder."))
                    else:
                        global dlm
                        dlm=E2.get()
                        root.destroy()
                        
    L1 = Label(root, text="Select data transfer within study vendor folder:").grid(row=0, column=0, columnspan=4, pady=3, sticky=W)
    E1 = Entry(root)
    E1.grid(row=1, column=0, columnspan=4, pady=(0,10), sticky=W+E)
    B1 = Button(root, text="Browse", command=doc_selection).grid(row=1, column=4, padx=(5,10), pady=(0,10))
            
    L2 = Label(root, text="Enter delimiter:").grid(row=2, column=0, columnspan=2, pady=3, sticky=W)
    E2 = Entry(root)
    E2.grid(row=3, column=0, sticky=W)
            
    B1 = Button(root, text="Done", command=done).grid(row=4, column=0, columnspan=5, pady=(25,5))
    
    root.geometry("+{}+{}".format(position_right, position_down))
    root.protocol("WM_DELETE_WINDOW", exit_function)
    root.mainloop()
    

def tk_close(title, message):
           
    root1 = Tk()
    root1.title(title)
          
    def exit_function():
        root1.destroy()
        sys.exit()
    
    # get height and width of screen to center window
    window_width = root1.winfo_reqwidth()
    window_height = root1.winfo_reqheight()
    
    position_right = int(root1.winfo_screenwidth()/2 - window_width/2)
    position_down = int(root1.winfo_screenheight()/2 - window_height/2)
    
    root1.geometry("+{}+{}".format(position_right, position_down))
    
    L1 = Label(root1, text=message)
    L1.pack()
    B1 = Button(root1, text="OK", command=exit_function)
    B1.pack()
    
    root1.mainloop()


tk_main()

# =============================================================================
# Folder/Document Locations
# =============================================================================

# input files
doc_conditions = os.path.join(folder_vendor, 'conditions.txt')
doc_lbtests    = os.path.join(folder_vendor, 'lbtests.txt')
doc_patterns   = os.path.join(folder_vendor, 'patterns.txt')
doc_vissched   = os.path.join(folder_vendor, 'vissched.txt')

# output file
dict_output  = defaultdict(dict)
dict_summary = defaultdict(list)

doc_output  = os.path.join(folder_vendor, 'output.txt')
doc_summary = os.path.join(folder_vendor, 'summary.txt')


# =============================================================================
# DTA Info Input
#  -- Create dictionaries with relevant info from lbtests.txt, vissched.txt, 
#     patterns.txt, and conditions.txt
#  -- Informs user if there is an error in any doc
# =============================================================================  

# -- lbtests
lbtest_vars = ['LABTYPE', 'LABTEST', 'SASLABNM', 'LBMETHOD', 'TSTCD', 'TSTNAM']
dict_lbtests = {}
with open(doc_lbtests, 'r', newline='') as obj_lbtests:
    reader_lbtests = csv.reader(obj_lbtests, delimiter='\t')
    next(reader_lbtests)  # skips header
  
    cur_line = 1    
    
    try:
        for labtype, labtest, saslabnm, lbmethod, tstcd, tstnam in reader_lbtests:
            
            labtype  = labtype.strip()
            labtest  = labtest.strip()
            saslabnm = saslabnm.strip()
            lbmethod = lbmethod.strip()
            tstcd    = tstcd.strip()
            tstnam   = tstnam.strip()
                       
            dict_lbtests[saslabnm] = {
                    'LABTYPE':  labtype,
                    'LABTEST':  labtest,
                    'LBMETHOD': lbmethod,
                    'TSTCD':    tstcd,
                    'TSTNAM':   tstnam
                    }

            cur_line += 1
    
    except ValueError as e:
        tk_close("Error", "ValueError: %s\n  Error found in lbtests.txt on line %s" % (e, cur_line))


# -- vissched
dict_vissched = {}
with open(doc_vissched, 'r', newline='') as obj_vissched:
    reader_vissched = csv.reader(obj_vissched, delimiter='\t')

    cur_line = 1    
    
    try:
        for visitlbl, visitnum in reader_vissched:
            dict_vissched[visitlbl] = visitnum

            cur_line += 1
            
    except ValueError as e:
        tk_close("Error", "ValueError: %s\n  Error found in vissched.txt on line %s in %s" % (e, cur_line, visitlbl))
        
    
# -- patterns
list_vars = []
dict_patterns = {}
with open(doc_patterns, 'r', newline='') as obj_patterns:
    reader_patterns = csv.reader(obj_patterns, delimiter='\t')
    
    cur_var = "first variable"
    cur_line = 1        
    
    try:
        for var, pattern in reader_patterns:
            dict_patterns[var] = pattern
            list_vars += [var]
            
            cur_var = var
            cur_line += 1

    except ValueError as e:
        tk_close("Error", "ValueError: %s\n  Error found in patterns.txt on line %s in %s" % (e, cur_line, cur_var))


# -- conditions
dict_conditions = defaultdict(list)
with open(doc_conditions, 'r', newline='') as obj_conditions:
    reader_conditions = csv.reader(obj_conditions, delimiter='\t')
    next(reader_conditions)

    cur_var = "first variable"    
    cur_line = 1    
    
    try:
        for var, condition, check in reader_conditions:
            dict_conditions[var].append((condition, check))

            cur_var = var
            cur_line += 1
            
    except ValueError as e:      
        tk_close("Error", "ValueError %s\n  Error found in conditions.txt on line %s in %s" % (e, cur_line, cur_var))

       
# =============================================================================
# Read Transfer
# =============================================================================

with open(doc_transfer, 'r', newline='') as obj_transfer:
    reader_transfer = csv.reader(obj_transfer, delimiter=dlm)
    next(reader_transfer)  # skips header
    
    transfer = {}  # dict containing each line in transfer's vars:values
    for line in reader_transfer:      
        row_num = reader_transfer.line_num - 1
        
        dict_output[row_num] = {}  # structure: 
                                   #   {row_num1: 
                                   #       {variable1: 
                                   #           [
                                   #              (invalid value1, pattern1, additional info1),
                                   #              (invalid value2, pattern2, additional info2)
                                   #           ]
                                   #        variable2:
                                   #           [
                                   #              (invalid value,  pattern,  additional info)
                                   #           ]
                                   #        }
                                   #    row_num2: ...
                                   #   }
        try:
            # initializes keys for each row and variable
            for i in range(len(list_vars)):
                var   = list_vars[i]  # e.g. INITIALS
                value = line[i]       # e.g. DBA
                
                transfer[var] = value    
                dict_output[row_num][var] = []  
        except IndexError:
            tk_close("Error", "Delimiter used may not be correct.\nPlease try again.")
            
        # fills dict_output with info about issues
        for var in transfer:
            
            # checks values against pattern
            if var not in lbtest_vars:
                try: 
                    pattern = dict_patterns[var]  # e.g. '^[A-Z]([A-Z]|-)[A-Z]$'
                    pattern_eval = "".join(eval(pattern))
                    
                    re_var = re.compile(pattern_eval)  
                    re_var_match = re_var.search(transfer[var])
                     
                    # saves info if value doesn't match pattern
                    if re_var_match == None:
                        dict_output[row_num][var].append((
                                transfer[var],  # invalid value
                                pattern_eval,   # pattern
                                ""              # additional info
                        ))             
                except SyntaxError:
                    tk_close("Error", "SyntaxError: %s\nError found in patterns.txt for variable %s." % (pattern, var))

            # more checks for lbtest variables
            else:     
                if dict_output[row_num]['SASLABNM'] != []:
                    continue
                
                elif transfer['SASLABNM'] not in dict_lbtests.keys():
                    dict_output[row_num]['SASLABNM'].append((
                            transfer['SASLABNM'],        # invalid value
                            "[Value not listed in DTA]", # pattern
                            "[LABTYPE:%s LABTEST:%s SASLABNM:%s LBMETHOD:%s TSTCD:%s TSTNAM:%s]"  # additional info
                              % (transfer['LABTYPE'], transfer['LABTEST'], transfer['SASLABNM'],
                                 transfer['LBMETHOD'], transfer['TSTCD'], transfer['TSTNAM'])
                    ))
                    
                elif var != 'SASLABNM' and transfer[var] != dict_lbtests[transfer['SASLABNM']][var]:
                    dict_output[row_num][var].append((
                            transfer[var],                            # invalid value
                            dict_lbtests[transfer['SASLABNM']][var],  # pattern - should match lbtest value
                            "[LABTYPE:%s LABTEST:%s SASLABNM:%s LBMETHOD:%s TSTCD:%s TSTNAM:%s]"  # additional info
                              % (transfer['LABTYPE'], transfer['LABTEST'], transfer['SASLABNM'],
                                 transfer['LBMETHOD'], transfer['TSTCD'], transfer['TSTNAM'])
                    ))

        # checks values against given condition
        for var, rules in dict_conditions.items():
            for rule in rules:
                condition = rule[0] 
                check     = rule[1]
                
                # skips check if condition is not met or causes an error
                try:
                    if not eval(condition):
                        continue
                    
                    if not eval(check):
                        dict_output[row_num][var].append((
                                transfer[var],       # invalid value
                                (condition, check),  # pattern
                                ""                   # additional info
                        ))
                         
                except ValueError:
                    continue


# create dict_summary dictionary
for row_num, var1 in dict_output.items():
    
    if not any(var1.values()):
        continue
        
    for var2, issues in dict_output[row_num].items():
        
        if (len(issues)) == 0:
            continue
        
        for issue in issues:
             variable      = var2
             pattern       = issue[1]
             row           = str(row_num)
             invalid_value = str(issue[0])
             info          = str(issue[2])
             
             key = str(variable) + str(pattern)
             
             if dict_summary[key] == []:
                 dict_summary[key].append(variable)
                 dict_summary[key].append(pattern)
             
             if len(dict_summary[key]) == 2:
                 dict_summary[key].append([])
                 dict_summary[key].append([])
                 if info != "":
                     dict_summary[key].append([])

             dict_summary[key][2].append(row)
             
             if invalid_value not in dict_summary[key][3]:
                 dict_summary[key][3].append(invalid_value)
                 
             if len(dict_summary[key]) == 5 and info not in dict_summary[key][4]:
                 dict_summary[key][4].append(info)

# =============================================================================
# Output
#   -- Creates output.txt and summary.txt files
# =============================================================================

# create output.txt file
with open(doc_output, 'w') as obj_output:

    message = ""
    
    # parses lines
    for row_num, var1 in dict_output.items():
        
        tracker_var = 0  # tracks number of variables with issues
        
        if not any(var1.values()):  # skip rows without issues
            continue
        
        message += "row " + str(row_num) + ": "
        len_header = len(str(row_num)) + 7  # length of header "row 1: "
        
        # parses variables + issues of each line
        for var2, issues in dict_output[row_num].items():
            
            if len(issues) == 0:
                continue
            
            tracker_var += 1
            
            # parses each issue within issues
            for idx, issue in enumerate(issues):
                
                invalid_value = issue[0]
                pattern       = issue[1]
                info          = issue[2]
                          
                if tracker_var > 1:
                    message += "\n" + len_header * " "
                    
                if idx == 0:
                    message += ("- %s invalid value [%s]" % (var2, invalid_value))
                
                if pattern != "" and type(pattern) == str:
                    message += ("\n" + (len_header + 4) * " " +
                               "*Pattern: %s" % (pattern)) 
                elif pattern != "" and type(pattern) == tuple:
                    condition = pattern[0]
                    check = pattern[1]
                    message += ("\n" + (len_header + 4) * " " +  
                                "*Ensure: %s, since: %s" % (check, condition))
            
                if info != "":                            
                    message += ("\n" + (len_header + 4) * " " +
                                "*Review: %s" % (info))
                            
        message += "\n\n"
    
    if message != "":
        obj_output.write(message)
    else:
        obj_output.write("No errors found")
    

# create summary.txt file
with open(doc_summary, 'w') as obj_summary:
    message = ""    
    for issue in dict_summary:
        
        variable       = dict_summary[issue][0]
        pattern        = dict_summary[issue][1]
        rows           = ",".join(dict_summary[issue][2])
        invalid_values = "][".join(dict_summary[issue][3])
        
        message += ("- %s invalid values:" % (variable) +
                    "\n    *Value: [%s]" % (invalid_values))
        
        if type(pattern) == str:
            message += "\n    *Violates/Pattern: %s" % (pattern)
        elif type(pattern) == tuple:
            condition = pattern[0]
            check = pattern[1]
            message += "\n    *Violates/Pattern: %s, since: %s" % (check, condition)
                       
        message += "\n    *Row: %s" % (rows)
        
        if len(dict_summary[issue]) == 5:
            info = "\n                           ".join(dict_summary[issue][4])
            message += ("\n    *Additionally, review: %s" % (info))
        
        message += "\n\n"
        
    if message != "":
        obj_summary.write(message)
    else:
        obj_summary.write("No errors found")
    
    
tk_close("Done", "Review is complete.")