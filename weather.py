import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime

# Configurações da API do OpenWeather
API_KEY = st.secrets["API_KEY"]
BASE_URL_WEATHER = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
BASE_URL_AIR_QUALITY = "https://api.openweathermap.org/data/2.5/air_pollution"
BASE_URL_ALERTS = "https://api.openweathermap.org/data/2.5/onecall"
BASE_URL_UV = "https://api.openweathermap.org/data/2.5/uvi"

# Níveis recomendados de poluentes (valores fictícios para exemplo)
RECOMMENDED_LEVELS = {
    'pm2_5': 25,  # µg/m³
    'pm10': 50,  # µg/m³
    'no2': 40,  # µg/m³
    'so2': 20,  # µg/m³
    'o3': 100,  # µg/m³
    'co': 450  # ppm
}

# Função para obter dados meteorológicos
def get_weather_data(city, country):
    params = {
        'q': f"{city},{country}",
        'appid': API_KEY,
        'units': 'metric',
        'lang': 'pt_br'
    }
    response = requests.get(BASE_URL_WEATHER, params=params)
    return response.json()

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

# Função para obter dados de qualidade do ar
def get_air_quality_data(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY
    }
    response = requests.get(BASE_URL_AIR_QUALITY, params=params)
    return response.json()

# Função para obter alertas meteorológicos
def get_alerts(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY,
        'exclude': 'minutely,hourly,daily',
        'units': 'metric',
        'lang': 'pt_br'
    }
    response = requests.get(BASE_URL_ALERTS, params=params)
    return response.json()

# Função para obter índice UV
def get_uv_index(lat, lon):
    params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY
    }
    response = requests.get(BASE_URL_UV, params=params)
    return response.json()

# Função para exibir a previsão do tempo
def display_forecast(city, country, date):
    forecast_data = get_forecast_data(city, country)
    if forecast_data.get("cod") != "200":
        st.error("Erro ao obter dados de previsão do tempo.")
    else:
        st.subheader(f"Previsão do Tempo para {date}")

        forecast_list = []
        for day in forecast_data['list']:
            if day['dt_txt'].startswith(date):
                forecast_list.append({
                    'Data': day['dt_txt'],
                    'Temperatura (°C)': day['main']['temp'],
                    'Descrição': day['weather'][0]['description'].capitalize()
                })

        if not forecast_list:
            st.warning("Nenhuma previsão encontrada para a data especificada.")
        else:
            forecast_df = pd.DataFrame(forecast_list)
            st.table(forecast_df)

# Função para exibir alertas meteorológicos
def display_alerts(lat, lon):
    alerts_data = get_alerts(lat, lon)
    if 'alerts' in alerts_data:
        st.subheader("Alertas Meteorológicos")
        for alert in alerts_data['alerts']:
            st.write(f"**{alert['event']}**")
            st.write(alert['description'])
            st.write(f"Início: {datetime.fromtimestamp(alert['start']).strftime('%d-%m-%Y %H:%M')}")
            st.write(f"Término: {datetime.fromtimestamp(alert['end']).strftime('%d-%m-%Y %H:%M')}")
    else:
        st.write("Sem alertas meteorológicos no momento.")

# Função para exibir índice UV
def display_uv_index(lat, lon):
    uv_data = get_uv_index(lat, lon)
    if uv_data:
        return uv_data['value']
    else:
        return None

# Função para exibir imagem com base no clima
def display_climate_image(weather_description):
    st.header("Aproveite o clima")
    if 'nublado' in weather_description or 'névoa' in weather_description or 'nuvens' in weather_description or 'nuvens dispersas' in weather_description or 'nublado' in weather_description:
        st.image('robo_nublado.png')
    elif 'sol' in weather_description or 'céu claro' in weather_description or 'céu limpo' in weather_description or 'ensolarado' in weather_description:
        st.image('robo_sol.png')
    elif 'chuva' in weather_description or 'chuvisco' in weather_description or 'pancada de chuva' in weather_description:
        st.image('robo_chuva.png')
    elif 'neve' in weather_description:
        st.image('robo_neve.png')

# Função para criar a dashboard
def create_dashboard():
    st.title('Dashboard de Saúde e Clima')

    # Adicionar entrada para cidade e país
    city = st.text_input("Digite o nome da cidade", "Rio de Janeiro")
    country = st.text_input("Digite o código do país (ex: br, us, ca)", "br")
    
    if city and country:
        # Remover espaços extras e capitalizar o nome da cidade
        city = city.strip().title()
        country = country.strip().lower()
        weather_data = get_weather_data(city, country)
        
        if weather_data.get("cod") != 200:
            st.error(f"Cidade '{city}' não encontrada no país '{country.upper()}'. Tente outra cidade ou país.")
        else:
            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']
            air_quality_data = get_air_quality_data(lat, lon)
            uv_index = display_uv_index(lat, lon)

            st.subheader(f"**Dados do clima atual para {city}**")
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Temperatura:** {weather_data['main']['temp']} °C")
                st.write(f"**Umidade:** {weather_data['main']['humidity']}%")
                st.write(f"**Pressão:** {weather_data['main']['pressure']} hPa")
                st.write(f"**Velocidade do Vento:** {weather_data['wind']['speed']} m/s")
            with col2:
                st.write(f"**Descrição:** {weather_data['weather'][0]['description'].capitalize()}")
                st.write(f"**Índice UV:** {uv_index}")
                if uv_index and uv_index > 11:
                    st.warning("**Índice UV está extremamente alto! Proteja-se do sol.**")
                if air_quality_data:
                    st.write(f"**Qualidade do Ar:** {air_quality_data['list'][0]['main']['aqi']}")
                else:
                    st.write("**Qualidade do Ar:** N/A")
            
            if air_quality_data:
                components = air_quality_data['list'][0]['components']
                components_df = pd.DataFrame(components.items(), columns=['Componente', 'Concentração'])

                # Verificar componentes acima dos níveis recomendados
                for component, concentration in components.items():
                    # Considerar ppm para CO e ajustar valores de referência
                    if component == 'co':
                        concentration_ppm = concentration / 1000  # Converter µg/m³ para ppm
                        if concentration_ppm > RECOMMENDED_LEVELS[component]:
                            st.warning(f"Nível de {component.upper()} está acima do recomendado: {concentration_ppm} ppm (Recomendado: {RECOMMENDED_LEVELS[component]} ppm)")
                    elif component in RECOMMENDED_LEVELS and concentration > RECOMMENDED_LEVELS[component]:
                        st.warning(f"Nível de {component.upper()} está acima do recomendado: {concentration} µg/m³ (Recomendado: {RECOMMENDED_LEVELS[component]} µg/m³)")

                # Exibir gráfico de componentes do ar
                st.subheader('Componentes da Qualidade do Ar')
                air_quality_chart = alt.Chart(components_df).mark_bar().encode(
                    x=alt.X('Componente:N'),
                    y=alt.Y('Concentração:Q'),
                    tooltip=['Componente', 'Concentração']
                ).properties(width=600, height=400).interactive()
                st.altair_chart(air_quality_chart)

            # Obter a descrição do clima atual
            weather_description = weather_data['weather'][0]['description'].lower()

            # Adicionar seleção de data
            date = st.date_input("Selecione uma data para a previsão", datetime.today())
            date_str = date.strftime("%Y-%m-%d")
            
            # Exibir previsão do tempo para a data selecionada
            display_forecast(city, country, date_str)
            # Exibir alertas meteorológicos
            display_alerts(lat, lon)

            # Exibir imagem com base no clima
            display_climate_image(weather_description)


if __name__ == "__main__":
    create_dashboard()

    # Adiciona um botão para atualização manual
    if st.button("Atualizar Dados"):
        st.rerun()
