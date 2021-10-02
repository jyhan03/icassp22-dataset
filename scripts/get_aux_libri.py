#!/bin/bash python3
"""
Created on Thu Jul 29 16:32:57 2021

@author: Jyhan
"""


import os
import random        

def get_info_dict(data_dir):
    """
    idir:
        original data root, egs: dev-clean
    return:
        wav_info, dict, wave_info[spk]=[wav1_path, wav2_path, wav3_path...]
    """
    wav_info = dict()
    entries = os.listdir(data_dir)
    for spk in entries:
        wav_name = []
        cdir = os.path.join(data_dir, spk)
        if os.path.isdir(cdir):
            g = os.walk(cdir)
            for path, _, wav_list in g:  
                for wav in wav_list:
                    if (wav.split('.')[-1] == 'flac'):
                        wav_name.append(os.path.join(path, wav))
            wav_info[spk] = wav_name    
    return wav_info
    
def get_aux(odir, lst, wav_info_dict):
    """
    odri:
        output dir, will wirte in odir/aux.lst
    lst:
        mixture speech name list file, 
        each line should be like "1272-128104-0000_2035-147961-0014.wav"   
    wav_info_dict:
        wav_info_dict[spk]=[wav1_path, wav2_path, wav3_path...]
    """  
    f = open(lst, 'r')
    aux_list = []
    for line in f:
        while (True):
            spk1 = line.split('_')[0].split('-')[0]
            spk1_wav = line.split('_')[0] + ".flac"
            aux1 = wav_info_dict[spk1][random.randint(0, len(wav_info_dict[spk1])-1)]
            aux1_name = aux1.split("/")[-1]
            
#            spk2 = line.split('_')[1].split('-')[0]
#            spk2_wav = line.split('_')[1].split('.')[0] + ".flac"   
#            aux2 = wav_info_dict[spk2][random.randint(0, len(wav_info_dict[spk2])-1)]
#            aux2_name = aux2.split("/")[-1]            
   
            if aux1_name != spk1_wav:
                aux_list.append(aux1)
                break
    if not os.path.exists(odir):        
        os.makedirs(odir) 
    odir = os.path.join(odir, "tt_aux.lst")
    with open(odir, 'w') as f:
        for aux in aux_list:
            f.write(aux+'\n')      
    
if __name__ == "__main__":
    data_dir = r"../test-clean"
    odir = r"./lst"
    lst = r"./lst/tt.lst"
    wav_info_dict = get_info_dict(data_dir)
    get_aux(odir, lst, wav_info_dict)
