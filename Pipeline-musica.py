import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# --- CONFIGURACIÓN ---
# ¡Reemplaza esto con tus propios datos!
LASTFM_API_KEY = "1b82f5f1b8b366467a90fb266ba8e791"  # Pega tu API Key aquí
LASTFM_USER = "manymanyto" # El usuario del que quieres los datos


# 1. La URL correcta del servicio de API
url = 'http://ws.audioscrobbler.com/2.0/'


payload = {
    'method': 'user.getTopArtists',  # <-- ¿Qué método usamos?
    'user': LASTFM_USER,      # <-- ¿Qué variable va aquí?
    'api_key': LASTFM_API_KEY,   # <-- ¿Qué variable va aquí?
    'format': 'json'
}

print(f"llamando a la api para obetener los artistas mas escuchados por {LASTFM_USER}")

# 4. La llamada
response = requests.get(url, params=payload)

print("¡Respuesta recibida!")

# 5. La conversión
data = response.json()

df = pd.json_normalize(
    data, 
    record_path=['topartists', 'artist']  # <-- ¡Ese es el camino!
)

#dataframe limpio
df_clean = df[['name', 'playcount', '@attr.rank']]

df_clean = df_clean.rename(columns={
    '@attr.rank': 'Rank',
    'name': 'Nombre',
    'playcount': 'Reproducido'
})

#Cambiamos el tipo de dato
df_clean['Reproducido'] = df_clean['Reproducido'].astype(int)
df_clean['Rank'] = df_clean['Rank'].astype(int)


# Tu código aquí
#artistas_populares = df_clean[ df_clean['Reproducido'] > 3 ]

df_clean['extraction_date'] = datetime.now()


print(df_clean.head(20))



from sqlalchemy import create_engine
from urllib.parse import quote_plus  # <--- 1. IMPORTANTE: Agrega esto arriba

# ... (tu código anterior) ...

# --- CONFIGURACIÓN DE LA BD ---
DB_USER = "postgres"
DB_PASS = "1234"  # Pon aquí tu contraseña tal cual es (con tildes o ñ)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_music"



print("Construyendo la dirección de forma segura...")



url_conexion = URL.create(
    drivername="postgresql",
    username=DB_USER,
    password=DB_PASS,  
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

engine = create_engine(url_conexion)

print("Conectando...")

print("Cargando datos...")

print("Inicio de proceso --IDEMPOTENCIA--")

#Definir fecha de hoy
fecha_hoy = datetime.now().date()
print(f"Fecha de proceso {fecha_hoy}")

Query_delete_time = text(f"""
    DELETE FROM TOP_ARTISTS
    WHERE extraction_date::DATE = '{fecha_hoy}'
""")

with engine.connect() as connection:
    print("Buscando y borrando datos manipulados HOY")
    connection.execute(Query_delete_time)
    connection.commit()
    print("Limpieza completada")


print("Fin de proceso de limpieza")

df_clean.to_sql(
    name='top_artists', 
    con=engine,         
    if_exists='append', 
    index=False         
)

print("¡Éxito! Los datos han sido guardados en la bodega.")