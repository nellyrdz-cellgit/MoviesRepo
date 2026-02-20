import pandas as pd
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json

# ---------------- CONEXIÓN A FIRESTORE ----------------
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-199f4")
dbMovies = db.collection("movies")

# ---------------- CARGAR DATASET BASE ----------------
@st.cache_data
def load_movies():
    docs = dbMovies.stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)

movies_df = load_movies()

# ---------------- TÍTULO ----------------
st.title("Lista de Películas")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Visualización")
show_all = st.sidebar.checkbox("Mostrar todos los filmes")

# ---- Buscar por título ----
st.sidebar.header("Buscar por título")
title_search = st.sidebar.text_input("Título del filme")
search_btn = st.sidebar.button("Buscar")

# ---- Filtro por director ----
st.sidebar.header("Filtrar por director")

if "director" in movies_df.columns and not movies_df.empty:
    directors_list = sorted(movies_df["director"].dropna().unique())
    selected_director = st.sidebar.selectbox(
        "Selecciona un director", 
        ["-- Seleccionar --"] + list(directors_list)
    )
    search_director_btn = st.sidebar.button("Buscar por director")
else:
    selected_director = None
    search_director_btn = False
    st.sidebar.write("No hay directores disponibles")

# ---- Crear nueva película ----
st.sidebar.markdown("------------------------------")
st.sidebar.header("Nueva película")

name = st.sidebar.text_input("Nombre de la película")
filemcompany = st.sidebar.text_input("Compañía Cinematográfica")
director = st.sidebar.text_input("Director")
genre = st.sidebar.text_input("Género")

submit = st.sidebar.button("Crear nueva película")

if submit:
    if name and filmcompany and director and genre:
        new_movie = {
            "name": name,
            "filmcompany": filmcompany,
            "director": director,
            "genre": genre
        }

        # Guardar en Firestore
        dbMovies.add(new_movie)

        # Agregar al DataFrame en memoria
        movies_df.loc[len(movies_df)] = new_movie

        st.sidebar.success("Película agregada correctamente")
    else:
        st.sidebar.warning("Completa todos los campos")
        

# ---------------- MOSTRAR RESULTADOS ----------------
st.markdown("------------------------------")
st.subheader("Listado de películas")

# Mostrar todos
if show_all:
    if not movies_df.empty:
        st.dataframe(movies_df, use_container_width=True)
    else:
        st.write("No hay películas registradas")

# Buscar por título
elif search_btn and title_search:
    if "name" in movies_df.columns:
        filtered_df = movies_df[
            movies_df["name"].str.contains(title_search, case=False, na=False)
        ]

        if not filtered_df.empty:
            st.subheader("Resultados por título")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning("No se encontraron películas con ese título")

# Filtrar por director
elif search_director_btn and selected_director != "-- Seleccionar --":
    filtered_df = movies_df[movies_df["director"] == selected_director]

    if not filtered_df.empty:
        st.subheader(f"Películas de {selected_director}")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.warning("No hay películas para ese director")

# Vista por defecto
else:
    if not movies_df.empty:
        st.dataframe(movies_df, use_container_width=True)
    else:
        st.write("No hay películas registradas")
