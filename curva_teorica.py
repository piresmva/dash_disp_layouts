# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 21:21:03 2023

@author: Marcus
"""

#Módulos utilizados
import numpy as np
import math
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
# import webbrowser



#%% Grupo de Funções 02: Calculo da transmissão teórica

# Função para calcular abs(T)^2 para uma cavidade interna
def calculate_spectrum_for_1_internal_cavity(R0, A0, k0, R1, A1, k1, delta_phi1):
    Ng= 1.999
    
    L0= 2 * math.pi * R0
    Phi0= (2 * math.pi) / wavelength * Ng * L0
    t0= math.sqrt(1 - k0**2)
    
    L1= 2 * math.pi * R1
    Phi1= (2 * math.pi) / wavelength * (Ng + delta_phi1) * L1
    t1= math.sqrt(1 - k1**2)

    # Qtot= (math.pi / (lambda_i * 1e-9)) * Ng * L0 * math.sqrt(t0 * A0) / (1 - t0 * A0)
    # Cav= (t1 - A1 * (math.e**(1j * Phi1))) / (1 - t1 * A1 * (math.e**(1j * Phi1)))
    
    T_n1 = (-A0*(math.e**(1j*Phi0))) * ((-A1*(math.e**(1j*Phi1)))+t1)
    T_n2 = t0*(1-A1*(math.e**(1j*Phi1))*t1)

    T_d1 = 1 - A1 * (math.e**(1j*Phi1)) * t1
    T_d2 = (-A0 * (math.e**(1j*Phi0)))* t0 * (-A1*(math.e**(1j*Phi1)) + t1)

    T = (T_n1+T_n2)/(T_d1+T_d2)

    T_pot = abs(T)**2

    return T_pot

#%% Calculo Teórico

# Parâmetros
R0 = 40
A0 = 0.951
k0 = 0.335
R1 = 25
delta_phi1 = 0
A1 = 0.95
k1 = 0.528
Ng= 1.999

# Valores iniciais
lambda_i = 1.46
lambda_f = 1.62
wavelength = np.arange(lambda_i, lambda_f, 0.00001)

# Crie o gráfico inicial
T_pot = calculate_spectrum_for_1_internal_cavity(R0, A0, k0, R1, A1, k1, delta_phi1)
trace2 = go.Scatter(x=wavelength, y=T_pot, mode='lines', name='Theoretical')

layout = go.Layout(
    xaxis={'title': 'Wavelength (nm)'},
    yaxis={'title': 'Normalized Transmission (a. u.)'},
    title='Transmission Spectrum'
)

#Cria a curva 2 com os dados teóricos
fig = go.Figure(data=[trace2], layout=layout)

#%% Criaçao do aplicativo Dash
app = dash.Dash(__name__)
server = app.server
#Layout dos controladores
app.layout = html.Div([
    dcc.Graph(id='spectrum-plot', figure=fig, style={'height': '800px'}),
    # html.Div([
    #     html.Label('Delta_x'),
    #     dcc.Input(id='deltax-input', type='number', value=deltax, step=0.0001)
    # ], style={'width': '20%', 'display': 'inline-block'}),
    
    html.Div([
        html.Div([
            html.Label('R0'),
            dcc.Input(id='R0-input', type='number', value=R0, step=1)
        ], style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Label('A0'),
            dcc.Input(id='A0-input', type='number', value=A0, step=0.01),
        ], style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Label('K0'),
            dcc.Input(id='K0-input', type='number', value=k0, step=0.01),
        ], style={'width': '20%', 'display': 'inline-block'}),
    ]),
    
    html.Div([
        html.Div([
            html.Label('R1'),
            dcc.Input(id='R1-input', type='number', value=R1, step=1)
        ], style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Label('A1'),
            dcc.Input(id='A1-input', type='number', value=A1, step=0.01),
        ], style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Label('K1'),
            dcc.Input(id='K1-input', type='number', value=k1, step=0.01),
        ], style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Delta Phi1'),
            dcc.Input(id='dphi1-input', type='number', value=delta_phi1, step=0.0001),
        ], style={'width': '20%', 'display': 'inline-block'}),
    ]),    
])

# Atualize o gráfico com base nos valores dos controles deslizantes e no intervalo de comprimento de onda selecionado
@app.callback(
    Output('spectrum-plot', 'figure'),
    # Input('deltax-input', 'value'),
    
    Input('R0-input', 'value'),
    Input('A0-input', 'value'),
    Input('K0-input', 'value'),    
    
    Input('R1-input', 'value'),
    Input('A1-input', 'value'),
    Input('K1-input', 'value'),
    Input('dphi1-input', 'value')
    
)
def update_plot(R0, A0, k0, R1, A1, k1, delta_phi1):
    # deltax = float(deltax)
    T_pot = calculate_spectrum_for_1_internal_cavity(R0, A0, k0, R1, A1, k1, delta_phi1)
    # trace1 = go.Scatter(x=(np.array(dados[:, 0])+deltax), y=dados[:, 1], mode='lines', name='Simulated')
    trace2 = go.Scatter(x=wavelength, y=T_pot, mode='lines', name='Theoretical')    
    layout = go.Layout(
        xaxis={'title': 'Wavelength (nm)'},
        yaxis={'title': 'Normalized Transmission (a. u.)'},
        title='Transmission Spectrum'
    )
    fig = go.Figure(data=[trace2], layout=layout)
    return fig

#%% Inicia o servidor Dash
if __name__ == '__main__':
    # Configure o endereço e a porta desejados
    host = '127.0.0.1'  # Ou o endereço desejado
    port = 8050  # A porta desejada

    # Abra o navegador automaticamente no endereço e porta configurados
    # webbrowser.open(f'http://{host}:{port}')

    # Inicie o servidor Dash
    app.run_server(host=host, port=port, debug=True)

