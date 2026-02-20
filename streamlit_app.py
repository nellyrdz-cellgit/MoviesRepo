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

st.sidebar.header("Buscar por título de filme")
title_search = st.sidebar.text_input("Título del filme")
search_btn = st.sidebar.button("Buscar")

st.sidebar.markdown("------------------------------")
st.sidebar.header("Nueva película")

name = st.sidebar.text_input("Nombre de la película")
filmcompany = st.sidebar.text_input("Compañía Cinematográfica")
director = st.sidebar.text_input("Director")
genre = st.sidebar.text_input("Género")

submit = st.sidebar.button("Crear nueva película")

if submit:
    if name and filmcompany and director and genre:
        dbMovies.add({
            "name": name,
            "filmcompany": filmcompany,
            "director": director,
            "genre": genre
        })
        st.sidebar.success("Película agregada correctamente")
        st.cache_data.clear()
        st.rerun()
    else:
        st.sidebar.warning("Completa todos los campos")

# ---------------- MOSTRAR RESULTADOS ----------------
st.markdown("------------------------------")
st.subheader("Listado de películas")

if show_all:
    if not movies_df.empty:
        st.dataframe(movies_df, use_container_width=True)
    else:
        st.write("No hay películas registradas")

elif search_btn and title_search:
    if "name" in movies_df.columns:
        filtered_df = movies_df[
            movies_df["name"].str.contains(title_search, case=False, na=False)
        ]

        if not filtered_df.empty:
            st.subheader("Resultados de búsqueda")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning("No se encontraron películas con ese título")
    else:
        st.warning("La base de datos no contiene la columna 'name'")

else:
    # Vista por defecto
    if not movies_df.empty:
        st.dataframe(movies_df, use_container_width=True)
    else:
        st.write("No hay películas registradas")
