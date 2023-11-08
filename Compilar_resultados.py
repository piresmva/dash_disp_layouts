# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 18:49:32 2023

@author: Marcus
"""

import numpy as np
import matplotlib.pyplot as plt
import re
import glob
from tqdm import tqdm

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import webbrowser
from dash.dependencies import Input, Output, Input, Output, State

global result_dict
global simulacoes_d1 
global simulacoes_d1

BASE_PATH = r'C:\Users\Marcus\Documents\Faculdade\Mestrado\Projeto\Simulacoes\Testes'

def ler_wmn(nome_arquivo):
    dados = []    
    with open(nome_arquivo, 'r') as arquivo:
        linhas = arquivo.readlines()
        for linha in linhas:
            if not linha.startswith('!'):
                valores = linha.split()
                dados.append([float(valores[0]), float(valores[1])])
    dados = np.array(dados)
    
    return dados

def recortar_regiao(vetor,lim_inf,lim_sup):
    dados_filtrados = vetor[(vetor[:, 0] >= lim_inf) & (vetor[:, 0] <= lim_sup)]
    
    return dados_filtrados

def normalizar_pot(vetor):
    max_value = max(vetor[:,1])
    for i in range(len(vetor[:,1])):
        vetor[i,1] = vetor[i,1]/max_value
    return vetor

def ler_sim_info(base_path):
    name = base_path.split('\\')[-1].replace("work","mainlog.txt")
    with open(base_path + rf"\{name}", "r") as arquivo:
        conteudo = arquivo.read()

    # Use regex para encontrar os valores de lo, hi, delta e steps
    padrao = r" (\d+)\) (\S+):  fixed steps, lo=([0-9.]+), hi=([0-9.]+), delta=([0-9.]+), steps=(\d+)"
    correspondencias = re.search(padrao, conteudo)
    
    # Verifique se houve correspondências
    if correspondencias:
        info = {'gap': correspondencias.group(2),
                'lo' : float(correspondencias.group(3)),
                'hi' : float(correspondencias.group(4)),
                'delta' : float(correspondencias.group(5)),
                'steps' : int(correspondencias.group(6))}
        # print(f"{name} - lo: ", info['lo']," hi: ",info ['hi'], " delta: ", info['delta'], " steps: ", info['steps'])
    
        info['range'] = np.arange(int(info['lo']*1000),int(info['hi']*1000)+int(info['delta']*1000),int(info['delta']*1000))
    else:
        print(f"{name} - Valores não encontrados no arquivo.")
        return False
    return info

def get_sim_parm_from_path(path):
    version_dcit={'V1':{'R0':50,'R1':25},
                  'V2':{'R0':35,'R1':20},
                  'V3':{'R0':30,'R1':20},
                  'V4':{'R0':30,'R1':10},
                  'V5':{'R0':38,'R1':20},
        }
    
    name = path.split('\\')[-1].replace("_work","")
    name_list = name.split("_")
    for val in name_list:
        if 'V' in val: 
            version = val
        elif 'GP' in val:
            gap = val
        try:
            gap_v = int(val)
        except ValueError:
            continue
        
    info ={'Waveguide_h': 0.5 if 'D2' in name_list else 0.3,
           'Waveguide_w': 0.7 if 'D2' in name_list else 0.9,
           'R0':version_dcit[version]['R0'],
           'R1':version_dcit[version]['R1'],
           'Gap1': gap_v if gap == 'GP1' else None,
           'Gap2': gap_v if gap == 'GP2' else None,
           'Sim_Name': name
        }
    
    return info

def get_sim_dict():
    SIM_PATHS = glob.glob(BASE_PATH+r'\**\*_work')
    
    result_dict = {}
    for idx, p in enumerate(SIM_PATHS):
    
        n_sim = len(SIM_PATHS)
        n_p = (idx+1)*100/n_sim
        
        info = ler_sim_info(p)
        if info == False:
            continue
        
        path_info = get_sim_parm_from_path(p)
        key = path_info['Sim_Name']
        result_dict[key]=dict()
        result_dict[key]['Header'] = path_info
        result_dict[key]['Sim_info'] = info
        
        result_dict[key]['Header'][info['gap']] = info['range']
        result_dict[key]['Data'] = dict()
        
        for i in tqdm(range(result_dict[key]['Sim_info']["steps"]), desc=f"Carregando Simulações {n_p:.2f}% "):
            
            nome_arquivo = p + rf"\raw\{key}_{i}.wmn"  
            try:
                dados = normalizar_pot(recortar_regiao(ler_wmn(nome_arquivo),1.51,1.59))
                result_dict[key]['Data'][i]= dados
            except FileNotFoundError:
                print(f'{nome_arquivo}, {result_dict[key]["Sim_info"]["steps"]} - Simulação incompleta')
                continue
            except Exception as e:
                print(f'Erro desconhecido: {e}')
                continue
    return result_dict

def update_result_dict(result_dict):
    SIM_PATHS = glob.glob(BASE_PATH+r'\**\*_work')
    for path in SIM_PATHS:
        name = path.split('\\')[-1].replace("_work","")
        
        info = ler_sim_info(path)
        if info == False:
            continue
        
        path_info = get_sim_parm_from_path(path)
        key = name
        
        if key not in result_dict.keys():
            print(f'Adicionando nova simulaçao: {key}')
            result_dict[key]=dict()        
            result_dict[key]['Header'] = path_info
            result_dict[key]['Sim_info'] = info
            
            result_dict[key]['Header'][info['gap']] = info['range']
            result_dict[key]['Data'] = dict()
        
        for i in range(result_dict[key]['Sim_info']["steps"]):
            if i not in result_dict[key]['Data'].keys():
                
            
                nome_arquivo = path + rf"\raw\{key}_{i}.wmn"  
                try:
                    dados = normalizar_pot(recortar_regiao(ler_wmn(nome_arquivo),1.51,1.59))
                    result_dict[key]['Data'][i]= dados
                    print(f'Adicionando novo resultado em {key}:{i}')
                except FileNotFoundError:
                    # print(f'{nome_arquivo}, {result_dict[key]["Sim_info"]["steps"]} - Simulação incompleta')
                    continue
                except Exception as e:
                    print(f'Erro desconhecido: {e}')
                    continue
            else:
                continue            
    # print('Escaneamento completo')
    return result_dict
    

# label_dip = 'R = [38;20]μm Gap_in 400nm and waveguide 0.3x0.9μm'
# label_leg = ['500nm', '600nm','700nm','800nm']

# plt.figure(figsize=(12, 6))
# for i in range(4):
#     nome_arquivo = BASE_PATH + rf"\D1\RR_V5_GP2_400_work\raw\RR_V5_GP2_400_{i}.wmn"    
#     dados = recortar_regiao(ler_wmn(nome_arquivo),1.46,1.62)    
#     plt.plot(dados[:, 0], dados[:, 1],label=label_leg[i])
    
# plt.xlabel('wavelength [μm]')
# plt.ylabel('Monitor Value [a.u]')
# plt.title(f'Response when varying the guide-cavity gap with the device: \n{label_dip}')
# plt.grid(True)
# plt.legend(loc='lower left')
# plt.show()

#%%

def obter_valor(simulacao_dict, simulacao_name):
    traces = []
    for i in simulacao_dict[simulacao_name]['Data'].keys():
        wavelength = simulacao_dict[simulacao_name]['Data'][i][:,0]
        T_pot = simulacao_dict[simulacao_name]['Data'][i][:,1]
        label_tex = simulacao_dict[simulacao_name]['Sim_info']['gap']
        label_var = simulacao_dict[simulacao_name]['Sim_info']['range'][i]
        traces.append(go.Scatter(x=wavelength, y=T_pot, mode='lines', name=f'{label_tex}:{label_var}'))
    
    return traces
    
result_dict = get_sim_dict()
simulacoes_d1 = sorted([key for key in list(result_dict.keys()) if 'D2' not in key])
simulacoes_d2 = sorted([key for key in list(result_dict.keys()) if 'D2' in key])
#%%
# sorted(list(result_dict.keys()))

# Inicialização do aplicativo Dash
app = dash.Dash(__name__)
app = app.server

# Crie o gráfico inicial
trace1 = obter_valor(result_dict, simulacoes_d1[0])
trace2 = obter_valor(result_dict, simulacoes_d2[0])

layout = go.Layout(
    xaxis={'title': 'Wavelength (nm)'},
    yaxis={'title': 'Normalized Transmission (a. u.)'},
    title='Transmission Spectrum'
)
fig1 = go.Figure(data=trace1, layout=layout)
fig2 = go.Figure(data=trace2, layout=layout)

# Layout do aplicativo
app.layout = html.Div([
       
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='tipo1-grafico',
                options=[{'label': tipo, 'value': tipo} for tipo in simulacoes_d1],
                value=simulacoes_d1[0]
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='tipo2-grafico',
                options=[{'label': tipo, 'value': tipo} for tipo in simulacoes_d2],
                value=simulacoes_d2[0]
            ),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id='grafico1', figure=fig1, style={'height': '600px'}),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([    
            dcc.Graph(id='grafico2', figure=fig2, style={'height': '600px'})
        ], style={'width': '50%', 'display': 'inline-block'}),
    ]),
    html.Div([
        html.Div(id='contador-output', children='Contador: 0'),
        html.Div(id='contador-zerado', children=''),
    ]),
    dcc.Interval(
        id='interval-component',
        interval= 10* 60 * 1000,  # Intervalo em milissegundos (1 segundo)
        n_intervals=0  # Inicializa o contador de intervalos
    )
])

contador = 0

# Função para atualizar o gráfico com base na seleção da lista suspensa
@app.callback(
    Output('grafico1', 'figure'),
    Output('grafico2', 'figure'),
    Input('tipo1-grafico', 'value'),
    Input('tipo2-grafico', 'value'),
    Input('interval-component', 'n_intervals')
)
def atualizar_grafico(selected_tipo1, selected_tipo2, n_intervals):
    global result_dict
    
    trace1 = obter_valor(result_dict, selected_tipo1)
    trace2 = obter_valor(result_dict, selected_tipo2)
    layout = go.Layout(
        xaxis={'title': 'Wavelength (nm)'},
        yaxis={'title': 'Normalized Transmission (a. u.)'},
        title='Transmission Spectrum'
    )

    fig1 = go.Figure(data=trace1, layout=layout)
    fig2 = go.Figure(data=trace2, layout=layout)

    return fig1, fig2

@app.callback(
    Output('contador-output', 'children'),
    Output('contador-zerado', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_counter(n_intervals):
    global contador
    global result_dict
    global simulacoes_d1
    global simulacoes_d2
    
    contador = (contador + 1) if contador != 1 else 0
    
    if contador == 0:
        result_dict = update_result_dict(result_dict)
        simulacoes_d1 = sorted([key for key in list(result_dict.keys()) if 'D2' not in key])
        simulacoes_d2 = sorted([key for key in list(result_dict.keys()) if 'D2' in key])
        return f'Contador: {contador}', 'Contador zerado'
    else:
        return f'Contador: {contador}', ''

if __name__ == '__main__':
    # Configure o endereço e a porta desejados
    host = '127.0.0.1'  # Ou o endereço desejado
    port = 8050  # A porta desejada

    # Abra o navegador automaticamente no endereço e porta configurados
    webbrowser.open(f'http://{host}:{port}')

    # Inicie o servidor Dash
    app.run_server(host=host, port=port, debug=True)
