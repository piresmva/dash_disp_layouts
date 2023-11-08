# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 16:06:40 2023

@author: Marcus
"""

import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def add_line(df, mode, w, s, i_2d, i_3d, C):
    '''
    df : Enter the dataframe to be updated.
    mode : mode TE or TM. 
    w : wavelength value.
    s : slab result.
    i_2d : neff 2d result.
    i_3d : neff 3d result.
    C : calculated correlation value.

    Returns -> df : DataFrame, updated data frame.
    '''
    new_l = pd.DataFrame({'Mode': [mode], 'wavelength': [w], 'slab': [s], 
                          'index_2d': [i_2d], 'index_3d': [i_3d], 'C': [C]})
    df = pd.concat([df, new_l], ignore_index=True)
    
    return df

def ler_dat(path):
    '''
    path : str, path to the .dat file resulting from the simulation.
    Returns -> data_dict : dict, dictionary with the wavelength and index values resulting from the simulation.
    '''
    try:
        with open(path, 'r') as arq:
            v = [[float(l.split()[0]),float(l.split()[1])] for l in arq]
        
        data_dict = {'wavelength': [v[i][0] for i in range(len(v))],
                     'index': [v[i][1] for i in range(len(v))]}        
    
    except FileNotFoundError:
        print(f"O arquivo {path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
    
    return data_dict

def get_str_path(path):
    '''
    path : str path to the .dat file resulting from the simulation.
    Returns -> keys : list of keys that describe the simulation.
    '''
    v = path.split('\\')
    keys = [v[-7], v[-6], v[-5], v[-4], v[-3][-7:-5]]
    
    return keys

#%%
EIM_SIM_PATH = r'C:\Users\Marcus\Documents\Faculdade\08_IC_2023_2024\Simulacoes\Redução 2D'
XSLX_PATH = r'C:\Users\Marcus\Documents\Faculdade\Mestrado\Projeto\Resumo Simulacoes'

MATERIAL_FOLDER = 'Si3Nx'
FOLDERS = ['Simulacao Neff 2D','Simulação Neff 3D','Simulacao Slab']
LAYOUTS = ['D1','D2']
MATERIAL = ['Si3Nx', 'Si3N4']
MODES = ['TM','TE']
TEMP = ['20','25','30','35','40']

slab_paths = glob.glob(EIM_SIM_PATH+r'\Si3Nx\Simulacao Slab\*\*\*\*\results\*mode_neffc.dat')
nf2d_paths = glob.glob(EIM_SIM_PATH+r'\Si3Nx\Simulacao Neff 2D\*\*\*\*\results\*mode_neffc.dat')
nf3d_paths = glob.glob(EIM_SIM_PATH+r'\Si3Nx\Simulação Neff 3D\*\*\*\*\results\*mode_neffc.dat')

#%%
r_d = {l: {m: {mode: {t: {'s': None, '2d': None, '3d': None} for t in TEMP} for mode in MODES} for m in MATERIAL} for l in LAYOUTS}

paths = [slab_paths, nf2d_paths, nf3d_paths]
keys = ['s', '2d', '3d']

for path_list, key in zip(paths, keys):
    for path in path_list:
        path_keys = get_str_path(path)
        r_d[path_keys[1]][path_keys[2]][path_keys[3]][path_keys[4]][key] = path
    
#%%  
df = pd.DataFrame(columns=['Mode', 'wavelength', 'slab', 'index_2d', 'index_3d', 'C'])

r_df_d = dict()
for l in LAYOUTS:
    r_df_d[l] = dict()

    for m in MATERIAL:
        r_df_d[l][m] = dict()
    
        for t in TEMP:
            r_df_d[l][m][f'T{t}'] = df.copy()
        
            for mode in MODES:
                slab_result = ler_dat(r_d[l][m][mode][t]['s'])
                nf2d_result = ler_dat(r_d[l][m][mode][t]['2d'])
                nf3d_result = ler_dat(r_d[l][m][mode][t]['3d'])
                
                for i in range(len(slab_result['wavelength'])):
                    w = slab_result['wavelength'][i]
                    s = slab_result['index'][i]
                    i_2d = nf2d_result['index'][i]
                    i_3d = nf3d_result['index'][i]
                    C = np.around((1-(abs(i_3d-i_2d))/i_3d)*100,4)
                    
                    r_df_d[l][m][f'T{t}'] = add_line(r_df_d[l][m][f'T{t}'], mode, w, s, i_2d, i_3d, C)

#%%
from openpyxl import Workbook

for l in LAYOUTS:    
    for m in MATERIAL:
        file_name = XSLX_PATH + rf"\{l} EIM {m} em SiO2.xlsx"
        excel_file = file_name

        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            writer.book = Workbook()

            for t in TEMP:
                sheet_name = f"T{t}"
                df_result = r_df_d[l][m][f'T{t}']
                df_result.to_excel(writer, sheet_name=sheet_name, index=False)
#%%
for j,l in enumerate(LAYOUTS):
    for i,m in enumerate(MATERIAL):
        
        plt.figure(j*2+i+1, figsize=(10, 6))
        for t in TEMP:
            df_plot = r_df_d[l][m][f'T{t}']
        
            # Filtrar os dados para as quatro séries que você deseja plotar
            tm_index_2d = df_plot[(df_plot['Mode'] == 'TM')]['index_2d']
            tm_index_3d = df_plot[(df_plot['Mode'] == 'TM')]['index_3d']
            te_index_2d = df_plot[(df_plot['Mode'] == 'TE')]['index_2d']
            te_index_3d = df_plot[(df_plot['Mode'] == 'TE')]['index_3d']
            wavelength  = df_plot[(df_plot['Mode'] == 'TE')]['wavelength']

            # Plotar o gráfico
            plt.plot(wavelength, tm_index_2d, label=f'TM - NEFF_2D {t}°C', linestyle='-')
            plt.plot(wavelength, tm_index_3d, label=f'TM - NEFF_3D {t}°C', linestyle='-', marker='s')
            plt.plot(wavelength, te_index_2d, label=f'TE - NEFF_2D {t}°C', linestyle='--')
            plt.plot(wavelength, te_index_3d, label=f'TE - NEFF_3D {t}°C', linestyle='--', marker='*')
            
            y_max = np.max(df_plot[(df_plot['Mode'] == 'TE')]['index_2d']) + 0.1
            y_min = np.min(df_plot[(df_plot['Mode'] == 'TM')]['index_2d']) - 0.05

        title_l = 'h: 0.5 w: 0.7' if l =='D1' else 'h: 0.3 w: 0.9'  

        plt.xlabel('Wavelength')
        plt.ylabel('Index Value')
        plt.title(f'EIM for waveguide {title_l} [µm] with {m} in SiO2')
        plt.ylim(y_min, y_max)
        legenda = plt.legend(loc='upper center', ncol=4)
        plt.setp(legenda.texts, size='8')
        plt.grid(True)

        plt.savefig(XSLX_PATH + rf'\grafico_{l}_{m}_{t}.png')
        # Exibir o gráfico
        plt.show()
