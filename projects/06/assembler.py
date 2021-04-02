#!/usr/bin/env python
# coding: utf-8

# In[1]:


symbolTable = {
    'R0' : 0,
    'R1' : 1,
    'R2' : 2,
    'R3' : 3,
    'R4' : 4,
    'R5' : 5,
    'R6' : 6,
    'R7' : 7,
    'R8' : 8,
    'R9' : 9,
    'R10' : 10,
    'R11' : 11,
    'R12' : 12,
    'R13' : 13,
    'R14' : 14,
    'R15' : 15,
    'SCREEN' : 16384,
    'KBD' : 24576,
    'SP' : 0,
    'LCL' : 1,
    'ARG' : 2,
    'THIS' : 3,
    'THAT' : 4
}


# In[2]:


destTable = {
    ''  : [],
    'M' : [12],
    'D' : [11],
    'A' : [10],
    'MD' : [11, 12],
    'AM' : [10, 12],
    'AD' : [10, 11],
    'AMD' : [10, 11, 12]
}


# In[3]:


compTable = {
    '0' : [4, 6, 8],
    '1' : [4, 5, 6, 7, 8, 9],
    '-1' : [4, 5, 6, 8],
    'D' : [6, 7],
    'A' : [4, 5],
    '!D' : [6, 7, 9],
    '!A' : [4, 5, 9],
    '-D' : [6, 7, 8, 9],
    '-A' : [4, 5, 8, 9],
    'D+1' : [5, 6, 7, 8, 9],
    'A+1' : [4, 5, 7, 8, 9],
    'D-1' : [6, 7, 8],
    'A-1' : [4, 5, 8],
    'D+A' : [8],
    'D-A' : [5, 8, 9],
    'A-D' : [7, 8, 9],
    'D&A' : [],
    'D|A' : [5, 7, 9],
    
    'M' : [3, 4, 5],
    '!M' : [3, 4, 5, 9],
    '-M' : [3, 4, 5, 8, 9],
    'M+1' : [3, 4, 5, 7, 8, 9],
    'M-1' : [3, 4, 5, 8],
    'D+M' : [3, 8],
    'D-M' : [3, 5, 8, 9],
    'M-D' : [3, 7, 8, 9],
    'D&M' : [3],
    'D|M' : [3, 5, 7, 9]
}


# In[4]:


jumpTable = {
    ''    : [],
    'JGT' : [15],
    'JEQ' : [14],
    'JGE' : [14, 15],
    'JLT' : [13],
    'JNE' : [13, 15],
    'JLE' : [13, 14],
    'JMP' : [13, 14, 15]
}


# In[5]:


class Assembler():
    def __init__(self, symbolTable, destTable, compTable, jumpTable):
        import copy
        self.symbolTable = copy.deepcopy(symbolTable)
        self.destTable = copy.deepcopy(destTable)
        self.compTable = copy.deepcopy(compTable)
        self.jumpTable = copy.deepcopy(jumpTable)
        
        self.var_cnt = 16
        self.prog = []
        self.line_cnt = 0
        
    def assemble(self, input_file, output_file=None):
        with open(input_file, 'r') as fp:
            for line in fp:
                line = line.strip().replace(" ", "")
                if len(line) == 0 or (line[0] == '/' and line[1] == '/'):
                    continue
                if line[0] == '(':
                    label_len = len(line)
                    self.symbolTable[line[1:label_len-1]] = self.line_cnt
                    continue
                self.prog.append(self.remove_comment(line))
                self.line_cnt = self.line_cnt + 1
        
#         print(self.prog)
        for line in self.prog:
            if self.is_acmd(line):
                if (line[1:].isdigit() == False) and (line[1:] not in self.symbolTable):
                    self.symbolTable[line[1:]] = self.var_cnt
                    self.var_cnt = self.var_cnt + 1
        
        if output_file is None:
            output_file = input_file.replace('.asm', '.hack')
        
        with open(output_file, 'w') as fp:
            for line in self.prog:
                if self.is_acmd(line):
        #             print(a_instruction_to_binary(line))
                    fp.write(self.a_instruction_to_binary(line) + '\n')
                else:
        #             print(c_instruction_to_binarwritee))
                    fp.write(self.c_instruction_to_binary(line) + '\n')
    
    def a_instruction_to_binary(self, line):
        if line[1:].isdigit():
            in_binary = bin(int(line[1:]))
        else:
            in_binary = bin(self.symbolTable[line[1:]])
        in_binary = list(in_binary)
        in_binary = in_binary[2:]  # removing '0b'
        in_binary = in_binary[-min(len(in_binary), 15):]
        in_binary = ['0'] * (16 - len(in_binary)) + in_binary
        return ''.join(in_binary)
    
    def c_instruction_to_binary(self, line):
        bin_res = ['0'] * 16
        bin_res[0] = '1'
        bin_res[1] = '1'
        bin_res[2] = '1'
        sps = line.split(';')
        for idx in self.c_cmd_eq(sps[0]):
            bin_res[idx] = '1'
        if len(sps) > 1:
            for idx in self.c_cmd_jmp(sps[1]):
                bin_res[idx] = '1'
        return ''.join(bin_res)

    def c_cmd_eq(self, eq_st):
        res = []
        dest = ""
        comp = ""
        if '=' in eq_st:
            dest, comp = eq_st.split('=')
        else:
            comp = eq_st
        for idx in self.compTable[comp]:
            res.append(idx)
        for idx in self.destTable[dest]:
            res.append(idx)
        return res
    
    def is_acmd(self, line):
        return line[0] == '@'
    
    def c_cmd_jmp(self, jmp_st):
        return self.jumpTable[jmp_st];
    
    def remove_comment(self, line):
        idx = line.find('//')
        if idx == -1:
            return line
        line = line[:idx]
        return line


# In[9]:


asm = Assembler(symbolTable, destTable, compTable, jumpTable)
asm.assemble('06/add/Add.asm')


# In[ ]:




