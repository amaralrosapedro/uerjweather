import streamlit as st
import requests
import pandas as pd
import altair as alt

# Configurações da API do OpenWeather
API_KEY = st.secrets["API_KEY"]
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"

# Função para obter previsão do tempo
def get_forecast_data(city, country):
    params = {
        'q': f"{city},{country}",
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'pt_br'
    }
    response = requests.get(BASE_URL_FORECAST, params=params)
    return response.json()

# Função para exibir a análise de previsão
def display_forecast_analysis(city, country):

    forecast_data = get_forecast_data(city, country)
    if forecast_data.get("cod") != "200":
        st.error("Erro ao obter dados de previsão do tempo.")
    else:
        forecast_list = []
        for day in forecast_data['list']:
            forecast_list.append({
                'Data': day['dt_txt'],
                'Temperatura (°C)': day['main']['temp'],
                'Descrição': day['weather'][0]['description'].capitalize()
            })

        forecast_df = pd.DataFrame(forecast_list)
        forecast_df['Data'] = pd.to_datetime(forecast_df['Data'])

        line_chart = alt.Chart(forecast_df).mark_line(color='blue').encode(
            x=alt.X('Data:T', title='Data', axis=alt.Axis(format='%d-%m-%Y')),
            y=alt.Y('Temperatura (°C):Q', title='Temperatura (°C)'),
            tooltip=['Data:T', 'Temperatura (°C):Q', 'Descrição:N']
        ).properties(
            width=800,
            height=400,
            title="Gráfico de Tendência de Previsão"
        ).configure_title(
            fontSize=20,
            font='Arial',
            anchor='start',
            color='blue'  # Título em azul
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14,
            labelColor='grey',
            titleColor='grey'
        ).interactive()

        st.altair_chart(line_chart)

def main():
    st.title('Análise de Tendência de Previsão')
    city = st.text_input("Digite o nome da cidade", "Rio de Janeiro")
    country = st.text_input("Digite o código do país (ex: br, us, ca)", "br")

    if city and country:
        display_forecast_analysis(city, country)

if __name__ == "__main__":
    main()
