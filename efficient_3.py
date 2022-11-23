import numpy as np
import os
import sys
from resource import *
import time
import psutil
import argparse

def generate_stings(input_file):
    """
    EFFICIENT functiont to generate 2 input strings from 2 base strings.

    Input: path for input file
    Output: a list with two generated strings
    """
    seq = input_file.read().split("\n") # read strings
    strings = [] # initialize return variable
    string = '' # initialize bubble variable
    i = 0 # initialize indices
    for s in seq:
        if not s.isdigit(): 
            if string == '': 
                string = s
                base_len = len(s) # store length for base 1
            else: 
                if base_len * 2 ** i != len(string): # check length for string 1
                    print("Error for string length.")
                    sys.exit(1)
                strings.append(string)
                string = s # resresh bubble
                i = 0 # refresh indices
                base_len = len(s) # store length for base 2
        else: 
            i += 1
            s = int(s)
            string = string[0:s+1] + string + string[s+1:]
    if base_len * 2 ** i != len(string): # check length for string 1
        print("Error for string length.")
        sys.exit(1)
    strings.append(string)
    return strings

def alignment_efficient(string1, string2): 
    """
    Function to align two strings (gap penalty and mismatch penalty are hardcoded).

    Inputs: two strings
    Outputs: the min cost for the alignment
             aligned string1
             aligned string2
    """
    code_dic = {"A": 1, "C": 2, "G": 3, "T": 5} # code ACGT 
    alpha = [0] * 26 # code alpha values in one dimention
    alpha[2], alpha[3], alpha[5], alpha[6], alpha[10], alpha[15] = 110, 48, 94, 118, 48, 110 # assign corresponding values
    delta = 30
    if len(string1) < 3 or len(string2) < 3: 
        dp = np.zeros((2, 2))
        for i in range(dp.shape[0]):  
            for j in range(dp.shape[1]): 
                if i == 0: # initialize 
                    dp[i, j] = j * delta
                    continue
                if j == 0: # initialize 
                    dp[i, j] = i * delta
                    continue
                dp[i, j] = min(dp[i - 1, j - 1] + alpha[code_dic[string1[i - 1]] * code_dic[string2[j - 1]]], # DP step
                            dp[i - 1, j] + delta, 
                            dp[i, j - 1] + delta)
        cost = int(dp[i, j])
        aligned1_back = ''
        aligned2_back = '' 
        while (i != 0) or (j != 0):
            if i == 0: # when string2 is longer
                aligned1_back += '_'
                aligned2_back += string2[j - 1]
                j -= 1
                continue
            if j == 0: # when string1 is longer
                aligned1_back += string1[i - 1]
                aligned2_back += '_'
                i -= 1
                continue
            diag_value = dp[i - 1, j - 1] + alpha[code_dic[string1[i - 1]] * code_dic[string2[j - 1]]] # traceback diagonal
            if diag_value == dp[i, j]: 
                aligned1_back += string1[i - 1]
                aligned2_back += string2[j - 1]
                i -= 1
                j -= 1
                continue
            if dp[i - 1, j] + delta == dp[i, j]: # traceback along string1
                aligned1_back += string1[i - 1]
                aligned2_back += '_'
                i -= 1
                continue
            if dp[i, j - 1] + delta == dp[i, j]: #traceback along string2
                aligned1_back += "_"
                aligned2_back += string2[j - 1]
                j -= 1
        aligned1 = aligned1_back[::-1] # get aligned string1
        aligned2 = aligned2_back[::-1] # get aligned string2
        return cost, aligned1, aligned2
    dp_l = np.zeros((2, len(string2) + 1))
    dp_r = np.zeros((2, len(string2) + 1))
    for i in range(len(string1) // 2 + 1): 
        for j in range(dp_l.shape[1]): 
            if i == 0:
                dp_l[i, j] = j * delta
                continue
            if j == 0:
                dp_l[1, 0] = i * delta
                continue
            dp_l[1, j] = min(dp_l[0, j - 1] + alpha[code_dic[string1[i - 1]] * code_dic[string2[j - 1]]], 
                            dp_l[0, j] + delta, 
                            dp_l[1, j - 1] + delta)
        for j in range(dp_l.shape[1]): 
            dp_l[0, j] = dp_l[1, j]
    for i in range(len(string1) - (len(string1) // 2) + 1): 
        for j in range(dp_r.shape[1]): 
            if i == 0: 
                dp_r[i, j] = j * delta
                continue
            if j == 0: 
                dp_r[1, 0] = i * delta
                continue
            dp_r[1, j] = min(dp_r[0, j - 1] + alpha[code_dic[string1[len(string1) - i]] * code_dic[string2[len(string2) - j]]], 
                            dp_r[0, j] + delta, 
                            dp_r[1, j - 1] + delta)
            for j in range(dp_l.shape[1]): 
                dp_r[0, j] = dp_r[1, j]
    cut_point = 0
    for j in range(dp_r.shape[1]): 
        if dp_l[0, j] + dp_r[0, len(string2) - j] < dp_l[0, cut_point] + dp_r[0, len(string2) - cut_point]: 
            cut_point = j
    cost = dp_l[0, cut_point] + dp_r[0, len(string2) - cut_point]
    aligned1_l, aligned2_l = alignment_efficient(string1[:(len(string1) // 2)], string2[:cut_point])
    aligned1_r, aligned2_r = alignment_efficient(string1[(len(string1) // 2):], string2[cut_point:])
    return cost, aligned1_l + aligned1_r, aligned2_l + aligned2_r

def process_memory():
    """
    Function to check consumed memory
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_consumed = int(memory_info.rss/1024)
    return memory_consumed

def run_alignment():
    parser = argparse.ArgumentParser() # parse in inputs
    parser.add_argument('input_path')
    parser.add_argument('output_path')
    args = parser.parse_args()
    start_time = time.process_time() # get the program starting time
    input_file = open(args.input_path)
    strings = generate_stings(input_file) # generate input stings
    string1 = strings[0]
    string2 = strings[1]
    cost, alignment1, alignment2 = alignment(string1, string2) # alignment
    end_time = time.process_time() # get the program endding time
    t = (end_time - start_time) * 1000
    mem = process_memory() # get memory
    output_file = open(args.output_path, 'w+')
    output_file.write(str(cost) + "\n" + alignment1 + "\n" + alignment2 + "\n" + str(t) + "\n" + str(mem))

if __name__ == '__main__':
    run_alignment()