# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 18:49:32 2023

@author: Marcus
"""

#import webbrowser
from dash.dependencies import Input, Output
import dash
import dash_core_components as dcc
import dash_html_components as html
import pickle  # Importe a biblioteca pickle para carregar o dicionário
import plotly.graph_objs as go

# Função para carregar o dicionário a partir do arquivo pickle
def carregar_result_dict():
    try:
        with open('result_dict.pkl', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        print("Arquivo result_dict.pkl não encontrado.")
        return {}  # Retorna um dicionário vazio se o arquivo não for encontrado
    
def obter_valor(simulacao_dict, simulacao_name):
    traces = []
    for i in simulacao_dict[simulacao_name]['Data'].keys():
        wavelength = simulacao_dict[simulacao_name]['Data'][i][:,0]
        T_pot = simulacao_dict[simulacao_name]['Data'][i][:,1]
        label_tex = simulacao_dict[simulacao_name]['Sim_info']['gap']
        label_var = simulacao_dict[simulacao_name]['Sim_info']['range'][i]
        traces.append(go.Scatter(x=wavelength, y=T_pot, mode='lines', name=f'{label_tex}:{label_var}'))
    
    return traces

result_dict = carregar_result_dict()
simulacoes_d1 = sorted([key for key in list(result_dict.keys()) if 'D2' not in key])
simulacoes_d2 = sorted([key for key in list(result_dict.keys()) if 'D2' in key])


# Inicialização do aplicativo Dash
app = dash.Dash(__name__)
server = app.server

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
        # result_dict = update_result_dict(result_dict)
        # simulacoes_d1 = sorted([key for key in list(result_dict.keys()) if 'D2' not in key])
        # simulacoes_d2 = sorted([key for key in list(result_dict.keys()) if 'D2' in key])
        return f'Contador: {contador}', 'Contador zerado'
    else:
        return f'Contador: {contador}', ''

if __name__ == '__main__':
    # Configure o endereço e a porta desejados
    host = '127.0.0.1'  # Ou o endereço desejado
    port = 8050  # A porta desejada

    # Abra o navegador automaticamente no endereço e porta configurados
    #webbrowser.open(f'http://{host}:{port}')

    # Inicie o servidor Dash
    app.run_server(host=host, port=port, debug=True)
