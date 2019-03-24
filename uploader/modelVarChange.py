#!/usr/bin/env python3

import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import re
import sympy
import argparse

m_eq_start = r'[ \-\^\+\(\*\/=\[]'
m_eq_end = r'[ \-\^\+\)\*\/;\]]'


parser = argparse.ArgumentParser(description='Python program for uploading matlab value of variables from .m file to simulink model')
parser.add_argument('-m','--mfile', help='.m file for uploading variables')
parser.add_argument('-in','--input', metavar='input',help='Input .slx file for uploading')
parser.add_argument('-out','--output', metavar='output',help='Output .slx file for uploading')

args = parser.parse_args()
input_filename=args.input;
output_filename=args.output;
file_var= args.mfile
tmp_folder = input_filename.split(".")[0]


zip_inp = zipfile.ZipFile(input_filename, 'r')
zip_inp.extractall(tmp_folder)
zip_inp.close()

cwd = os.getcwd()
listOfFiles = []

for dir_, _, files in os.walk(tmp_folder):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, tmp_folder)
        rel_file = os.path.join(rel_dir, file_name)
        listOfFiles.append(rel_file)

print("Unpack files and folders in slx: ")
for f in listOfFiles:
    print("     Unpack: "+ f)


# Parse matlab variables
f= open(file_var)
Value= []
list=[]
for line in f:
    match = re.findall(r'\S*\s*=\s*\S*;', line)
    for t in match:
        Value.append(t)
dictOfVar={}
for eq in Value:
    list_var = eq.strip(';');
    p=[l.strip() for l in list_var.split('=')]
    keys=dictOfVar.keys()
    for k in keys:
        find_var=k
        findObj=re.findall(m_eq_start+r'+[ ^,]?'+find_var+" ?"+m_eq_end+ '+' + r'|\b'+find_var+'{1}'+m_eq_end+ '+' + r'|'+ m_eq_start+'+'+find_var+'{1}'+ '\Z' + r'|\A'+ find_var+'{1}'+ '\Z', p[1])
        old_v = p[1]
        for obj in findObj:
            obj_new = obj.replace(k,str(dictOfVar[k]))
            new_v = old_v.replace(obj,obj_new)
            new_v = new_v.replace('^', '**')
            p[1]=new_v

    dictOfVar[p[0]]=sympy.N(p[1])
print("Solve equation with variables and export in simulink data:")
for k in dictOfVar.keys():
    print( "     "+k + " = " + str(dictOfVar[k]) )


#Replace variables in block
tree_block=ET.parse(tmp_folder+'/simulink/blockdiagram.xml')
rootb=tree_block.getroot()
for block in rootb.iter('Block'):
    if (block.attrib['BlockType']) == 'Gain' or (block.attrib['BlockType'])=='Constant' or (block.attrib['BlockType'])=='Integrator' or (block.attrib['BlockType'])=='TransferFcn' or (block.attrib['BlockType'])=='Step':
        for head_var in block:
            replace = False
            for k in dictOfVar.keys():
                find_var=k
                findObj=re.findall(m_eq_start+'+'+find_var+m_eq_end+ '+' + r'|\b'+find_var+'{1}'+m_eq_end+ '+' + r'|'+ m_eq_start+'+'+find_var+'{1}'+ '\Z' + r'|\A'+ find_var+'{1}'+ '\Z', head_var.text)
                if(findObj):
                    replace = True
                    old_head_var = head_var.text
                    for obj in findObj:
                        obj_old = obj.replace(find_var, str(dictOfVar[k]))
                        new_head_var = old_head_var.replace(obj,obj_old)
                        print("Change: "+head_var.text)
                        head_var.text=new_head_var
                        print("to "+head_var.text)
            if(replace):
                print("Simplify: " +head_var.text)
                if not(re.fullmatch(r'\[.*\]', head_var.text)):
                    head_var.text=str(sympy.N(head_var.text))
                print(" --> " + str(head_var.text))

#Replace variables in MATLAB Function
tree_func=ET.parse(tmp_folder+'/simulink/stateflow.xml')
rootf=tree_func.getroot()
stateflow=rootf[0]
for c in stateflow.iter('Children'):
    for child in c:
        for s in child.iter('state'):
            for fields in s:
                for eml in fields:
                    if eml.attrib['Name'] == 'script':
                        for k in dictOfVar.keys():
                            find_var=k
                            script_func =eml.text;
                            findObj=re.findall(m_eq_start+'+'+find_var+m_eq_end+ '+' + r'|\b'+find_var+'{1}'+m_eq_end+ r'+ ?[^=]' + r'|'+ m_eq_start+'+'+find_var+'{1}'+ '\Z' + r'|\A'+ find_var+'{1}'+ '\Z', eml.text)
                            for obj in findObj:
                                # print(obj)
                                obj_old = obj.replace(find_var, str(dictOfVar[k]))
                                script_func = script_func.replace(obj,obj_old)
                                # print("Change: " + eml.text)
                            eml.text=script_func

                            # findHeadObj=re.findall('= ?\D+\(.*,+.*\)', eml.text)
                            # for obj in findHeadObj:
                            #     # print(obj)
                            #     obj_old = re.sub(','+find_var+ ',', ",", obj)
                            #     obj_old = re.sub(','+find_var+ ' ,', "", obj_old)
                            #     obj_old = re.sub(','+find_var, "", obj_old)
                            #     obj_old = re.sub(find_var+",", "", obj_old)
                            #     obj_old = re.sub(' '+find_var+' ',"", obj_old)
                            #     script_func = script_func.replace(obj,obj_old)
                            #     # print("Change: " + eml.text)
                            # script_func = script_func.replace(',,','')
                            # # script_func = re.sub(' {3,}',' ', script_func)
                            # eml.text=script_func


tree_block.write(tmp_folder+'/simulink/blockdiagram.xml')
tree_func.write(tmp_folder+'/simulink/stateflow.xml')




with zipfile.ZipFile(output_filename, 'w') as zip_out:
    for f in listOfFiles:
        zip_out.write(tmp_folder+"/"+f, f)
    zip_out.close()
