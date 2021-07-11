#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import epitran
import numpy as np

def get_parser():
    parser = argparse.ArgumentParser(description="modify asr jsons to have two targets")
    parser.add_argument("--map-json", required=True, type=str)
    parser.add_argument("--phoneme-txt", required=True, type=str)
    parser.add_argument("--phone-txt", required=True, type=str)
    parser.add_argument("--nlsyms-txt", required=True, type=str)
    parser.add_argument("--output", required=True, type=str)
    return parser

args = get_parser().parse_args()

def main(args):

    xs = epitran.xsampa.XSampa()
    idx2phone = {}
    phone2phoneme = {}
    phoneme2idx = {}
    nlsyms = set()

    with open(args.phone_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for li in lines:
            name, idx = li.split()
            idx2phone[idx] = name
    print(idx2phone)
    with open(args.map_json, "r", encoding="utf-8") as f:
        map_data = json.load(f)
        for pair in map_data["mappings"]:
            #phone = xs.ipa2xs(pair["phone"])
            #phoneme = xs.ipa2xs(pair["phoneme"])
            phone = pair["phone"]
            phoneme = pair["phoneme"]
            if phone in phone2phoneme.keys():
                phone2phoneme[phone].append(phoneme)
            else:
                phone2phoneme[phone] = [phoneme]
    print(phone2phoneme) 
    with open(args.phoneme_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for li in lines:
            name, idx = li.split()
            phoneme2idx[name] = idx
    print(phoneme2idx) 
    with open(args.nlsyms_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for li in lines:
            name = li.strip()
            nlsyms.add(name)
    
    alloW = np.zeros((len(phoneme2idx.keys())+2, len(idx2phone.keys())+2))
    # first to first for blank, last to last for sos
    alloW[0][0] = 1.0
    alloW[1][1] = 1.0   #unk 
    alloW[-1][-1] = 1.0
    for i in range(1, alloW.shape[1]-1):
        phone = idx2phone[str(i)]
        if phone in nlsyms:
            alloW[i][i] = 1.0
        else:
            if phone in phone2phoneme.keys():
                for phoneme in phone2phoneme[phone]:
                    #phoneme = phone2phoneme[phone]
                    if phoneme in phoneme2idx.keys():
                        j = int(phoneme2idx[phoneme])
                        alloW[j][i] = 1.0
                    else:
                        print("many to one failed: " + phone)
            elif phone in phoneme2idx.keys():
                j = int(phoneme2idx[phone])
                alloW[j][i] = 1.0
            else:
                print("couldnt match: " + phone)
    print(alloW.shape)
    print(alloW.sum(axis=-1))
    alloW.dump(args.output)

if __name__ == "__main__":

    main(args)