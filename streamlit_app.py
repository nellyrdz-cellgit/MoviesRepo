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
else:
    selected_director = None
    st.sidebar.write("No hay directores disponibles")

# ---- Crear nueva película ----
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

# 1️⃣ Mostrar todos
if show_all:
    if not movies_df.empty:
