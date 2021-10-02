#!/bin/bash python3
"""
Created on Sun Aug 15 20:04:19 2021

@author: Jyhan
"""
import os
import math

import random
import librosa
import soundfile as sf

import argparse
import traceback

import numpy as np
import multiprocessing as mp

eps = np.finfo(np.float32).eps

def audioread(path, fs=8000):
    '''
    args
        path: wav path
        fs: sample rate
    return
        wave_data: L x C or L
    '''
    wave_data, sr = sf.read(path)
    if sr != fs:
        if len(wave_data.shape) != 1:
            wave_data = wave_data.transpose((1, 0))
        wave_data = librosa.resample(wave_data, sr, fs)
        if len(wave_data.shape) != 1:
            wave_data = wave_data.transpose((1, 0))
    return wave_data


def get_config_single(line, segment_length, sample_rate, result, snr_range=[-2.5,2.5]):
    """
    each line should be:
        /xxx/xxx/xxx.wav   /xxx/xxx/xxx.wav
    result:
        path1 start_idx end_idx path2 start_idx end_idx snr
    """
    try:
        path = line.split()
        data = [audioread(p, sample_rate) for p in path]
        length = [d.size for d in data]
        if segment_length < min(length):
            start_idx1 = random.randint(0, length[0] % segment_length)
            end_idx1 = start_idx1 + segment_length 
            start_idx2 = random.randint(0, length[1] % segment_length)
            end_idx2 = start_idx2 + segment_length   
            snr = random.uniform(*snr_range)
            result.append('{} {} {} {} {} {} {}\n'.format(path[0], start_idx1, end_idx1, \
                          path[1], start_idx2, end_idx2, snr))
    except :
#traceback.print_exc()
        print(path)
 
  
def get_config_mp(wav_path, conf_path, 
                   snr_range=[-2.5,2.5], 
                   sample_rate=8000, chunk_len=4, num_process=12):
    
    '''
    in_path contents should be:
        /xxx/xxx/xxx.wav   /xxx/xxx/xxx.wav
        /xxx/xxx/xxx.wav   /xxx/xxx/xxx.wav
        ...   
    out_path contents:
        path1 start_idx end_idx path2 start_idx end_idx snr
        path1 start_idx end_idx path2 start_idx end_idx snr
        ...
    '''
    lines = open(wav_path, 'r').readlines()

    pool = mp.Pool(num_process)
    mgr = mp.Manager()
    result = mgr.list()
    segment_length = int(sample_rate * chunk_len)

    for line in lines:
        pool.apply_async(
            get_config_single,
            args=(line, segment_length, sample_rate, result, snr_range)
            )
    pool.close()
    pool.join()
    wid = open(os.path.join(conf_path, 'tr_cfg.lst'), 'w')

    for item in result:
        wid.write(item)
    wid.close()    


def rms(data):
    """
    calc rms of wav
    """
    energy = data ** 2
    max_e = np.max(energy)
    low_thres = max_e*(10**(-50/10)) # to filter lower than 50dB 
    rms = np.mean(energy[energy>=low_thres])
    return rms


def snr_mix(clean, noise, snr):
    '''
    mix wav1 and wav2 according to snr
    '''
    clean_rms = rms(clean)
    clean_rms = np.maximum(clean_rms, eps)
    noise_rms = rms(noise)
    noise_rms = np.maximum(noise_rms, eps)
    k = math.sqrt(clean_rms / (10**(snr/10) * noise_rms))
    new_noise = noise * k
    return new_noise


def mix_func(line, dump_dir, sample_rate):
    try:
        path1, start_idx1, end_idx1, path2, start_idx2, end_idx2, snr = line.split()

        name1 = os.path.basename(path1).replace('.wav', '')
        name2 = os.path.basename(path2).replace('.wav', '')
        
        seg = '_'
        utt_id = name1 + seg + name2 + seg + str(np.round(float(snr), 4)) + '.wav'
        
        snr = float(snr)
        
        spk1 = audioread(path1, sample_rate)
        spk2 = audioread(path2, sample_rate)

        start_idx1 = int(start_idx1)
        end_idx1 = int(end_idx1)
        start_idx2 = int(start_idx2)
        end_idx2 = int(end_idx2)
        spk1 = spk1[start_idx1:end_idx1]
        spk2 = spk2[start_idx2:end_idx2]
        
        spk2 = snr_mix(spk1, spk2, snr)
        
        end = min(spk1.size, spk2.size)
        spk1 = spk1[:end]
        spk2 = spk2[:end]
        mix = spk1 + spk2
        
        max_amp = np.max([np.max(np.abs(mix)), np.max(np.abs(spk1)), np.max(np.abs(spk2))])
        mix = mix / max_amp * 0.9  
        spk1 = spk1 / max_amp * 0.9  
        spk2 = spk2 / max_amp * 0.9  
          
        sf.write(os.path.join(dump_dir, 'mix', utt_id), mix, sample_rate)
        sf.write(os.path.join(dump_dir, 'spk1', utt_id), spk1, sample_rate)
        sf.write(os.path.join(dump_dir, 'spk2', utt_id), spk2, sample_rate)
    except :
        traceback.print_exc()


def mix_func_mp(conf_path, dump_dir, sample_rate=8000, num_process=12):
    '''
    according to the config file to generate data and then save in save_dir
    '''
    lines = open(os.path.join(conf_path, 'tr_cfg.lst'), 'r')
    
    pool = mp.Pool(num_process)

    for line in lines:
        line = line.strip()
        # multiprocessing
        pool.apply_async(
                mix_func,
                args=(line, dump_dir, sample_rate)
            )
    pool.close()
    pool.join()
    lines.close()
    

def main(args):
    wav_path = args.wav_path 
    conf_path = args.conf_path 
    dump_dir = args.dump_dir 
    
    if not os.path.isdir(conf_path):
        os.makedirs(conf_path)
    if not os.path.isdir(dump_dir):
        os.makedirs(dump_dir)
    if not os.path.isdir(os.path.join(dump_dir, 'mix')):
        os.mkdir(os.path.join(dump_dir, 'mix'))
    if not os.path.isdir(os.path.join(dump_dir, 'spk1')):
        os.mkdir(os.path.join(dump_dir, 'spk1'))
    if not os.path.isdir(os.path.join(dump_dir, 'spk2')):
        os.mkdir(os.path.join(dump_dir, 'spk2'))

    print('LOG: preparing mix config')
    get_config_mp(wav_path, conf_path, 
              snr_range=args.snr_range, sample_rate=args.sample_rate, 
			  chunk_len=args.chunk_len, num_process=args.num_process)
    
    print('LOG: generating')
    mix_func_mp(conf_path, dump_dir, sample_rate=args.sample_rate, num_process=args.num_process)    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--wav_path',
        type=str,
        default='in_path',
        help='the list of wav to read'
        ) 
    parser.add_argument(
        '--conf_path',
        type=str,
        default='out_path',
        help='output dir of config file to write'
        )       
    parser.add_argument(
        '--dump_dir',
        type=str,
        default='generated_data',
        help='the dir to save generated_data'
        ) 
    parser.add_argument(
        '--snr_range',
        type=list,
        default=[0,5],
        help='snr range'
        ) 
    parser.add_argument(
        '--sample_rate',
        type=int,
        default=8000,
        help='sample rate'
        )   
    parser.add_argument(
        '--chunk_len',
        type=int,
        default=4,
        help='chunk length'
        )   
    parser.add_argument(
        '--num_process',
        type=int,
        default=12,
        help='num process'
        )     
    args = parser.parse_args()
    main(args)    
