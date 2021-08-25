#!/bin/bash python3
"""
Created on Mon Aug 16 19:15:46 2021

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
                    if (wav.split('.')[-1] == 'wav'):
                        wav_name.append(os.path.join(path, wav))
            wav_info[spk] = wav_name    
    return wav_info

def get_lst(out_path, lst_num, wav_info_dict, black_list=None):
    """
    out_path:
        output dir, will wirte in odir/xxx.lst
    lst_num:
        how many mixture to generate
    for xxx.lst, each line will be:
        /xxx/xxx/BAC009S0915W0493.wav   /xxx/xxx/BAC009S0916W0497.wav  
    wav_info_dict:
        wav_info_dict[spk]=[wav1_path, wav2_path, wav3_path...]
    """  
    wav_list = []
    all_list = []
    spk_list = list(wav_info_dict.keys())
    all_num = lst_num 
    while (lst_num):
        spk1_id = random.randint(0, len(spk_list)-1)
        spk1 = spk_list[spk1_id]
        spk1_wav = wav_info_dict[spk1][random.randint(0, len(wav_info_dict[spk1])-1)]
        
        while (True):
            spk2_id = random.randint(0, len(spk_list)-1)
            if spk2_id != spk1_id:
                break
            
        spk2 = spk_list[spk2_id]
        spk2_wav = wav_info_dict[spk2][random.randint(0, len(wav_info_dict[spk2])-1)]   
        spk_pair = spk1_wav + " " + spk2_wav+ "\n" 
        spk_pair2 = spk2_wav + " " + spk1_wav+ "\n" 
        if spk_pair not in all_list:
            wav_list.append(spk_pair)
            lst_num = lst_num - 1
        all_list.append(spk_pair)
        all_list.append(spk_pair2)
    
    assert len(wav_list) == all_num
    
    if not os.path.exists(out_path):        
        os.makedirs(out_path) 
        
    wid = open(os.path.join(out_path, 'train.lst'), 'w')
    for item in wav_list:
        wid.write(item)
    wid.close()      
            
def main(data_dir, out_path, lst_num):
    wav_info = get_info_dict(data_dir)
    get_lst(out_path, lst_num, wav_info, black_list=None)
    
if __name__ == "__main__":
    data_dir = r"/Share/hjy/data/aishell/data_aishell/wav/train"
    out_path = r"/Share/hjy/data/aishell/data_aishell/wav/mix_lst"
    lst_num = 45000
    main(data_dir, out_path, lst_num)
