import pandas as pd
import numpy as np
import streamlit as st

from google.cloud import firestore
from google.oauth2 import service_account

import json


#--Trae llaves pra base de datos de secrets
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-199f4")
dbMovies = db.collection('movies')

@st.cache_data
def load_movies():
    docs = dbMovies.stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)

movies_df = load_movies()

# Titulo
st.title("Lista de Películas")

#Todas las peliculas
st.sidebar.header("Visualización")
show_all = st.sidebar.checkbox("Mostrar todos los filmes")
# Mostrar resultados principales
if show_all:
    st.subheader("Listado completo de filmes")
    st.dataframe(movies_df, use_container_width=True)

elif search_btn and title_search:
    filtered_df = movies_df[
        movies_df["name"].str.contains(title_search, case=False, na=False)
    ]

    st.subheader("Resultados de búsqueda")
    st.dataframe(filtered_df, use_container_width=True)

#Buscar por titulo
st.sidebar.header("Buscar por título de filme")

title_search = st.sidebar.text_input("Título del filme")
search_btn = st.sidebar.button("Buscar")

if search_btn and title_search:
    filtered_df = movies_df[
        movies_df["name"].str.contains(title_search, case=False, na=False)
    ]

    st.subheader("Resultados de búsqueda")
    st.dataframe(filtered_df, use_container_width=True)


#Si escogio ver todos o filtrado
if show_all:
    st.subheader("Listado completo de filmes")
    st.dataframe(movies_df)

elif search_btn and title_search:
    filtered_df = movies_df[
        movies_df["name"].str.contains(title_search, case=False, na=False)
    ]

    st.subheader("Resultados de búsqueda")
    st.dataframe(filtered_df)

# Crea película
#  doc_ref = db.collection('movies').document(name)
#--
st.sidebar.header("Nueva película")

name = st.sidebar.text_input('Nombre de la película')
filemcompany = st.sidebar.text_input('Compañía Cinematográfica')
director = st.sidebar.text_input('Director')
genre = st.sidebar.text_input('Género')

submit = st.sidebar.button('Crear nueva película')

if name and filemcompany and director and genre and submit:
    doc_ref = dbMovies.document(name)
    doc_ref.set({
        'name': name,
        'filemcompany': filemcompany,
        'director': director,
        'genre': genre
    })
    st.sidebar.success('Película agregada')
#--
# Función obtener directores únicos
def getDirectors():
    docs = dbMovies.stream()
    directors = set()
    for doc in docs:
        data = doc.to_dict()
        if "director" in data:
            directors.add(data["director"])
    return sorted(list(directors))

# Función buscar por director
def loadByDirector(director):
    movies_ref = dbMovies.where(u'director', u'==', director).stream()
    return list(movies_ref)

# Sidebar - Buscar por Director
st.sidebar.subheader("Buscar películas por Director")

directors_list = getDirectors()

if directors_list:
    DirectorSearch = st.sidebar.selectbox("Director", directors_list)
else:
    DirectorSearch = None
    st.sidebar.write("No hay directores registrados")

btnFiltrar = st.sidebar.button("Filtrar")

filtered_movies = []

if btnFiltrar and DirectorSearch:

    docs = loadByDirector(DirectorSearch)

    if len(docs) == 0:
        st.warning("No existen películas del director en la base de datos")
    else:
        for doc in docs:
            filtered_movies.append(doc.to_dict())


##Eliminar
#st.sidebar.markdown("______________________________")
#btnEliminar = st.sidebar.button("Eliminar")

#if (btnEliminar):
#  deletename = loadByName(nameSearch)
#  if deletename is None:
#    st.sidebar.write("La película no existe en nuestra base de datos")
#  else:
#    dbMovies.document(deletename.id).delete()
#    st.sidebar.write("Película eliminada")

#st.sidebar.markdown("______________________________")

##Modificar
#newname = st.sidebar.text_input("Modificar nombre")
#btnModificar = st.sidebar.button("Modificar")

#if btnModificar:
#  updatename = loadByName(nameSearch)
#  if updatename is None:
#    st.sidebar.write("La película no existe en nuestra base de datos")
#  else:
#    myupdatename=dbMovies.document(updatename.id)
#    myupdatename.update({
#        'name': newname
#    })


## Listado  de películas
#st.markdown("______________________________")
#st.subheader("Listado de películas")

#if btnFiltrar and DirectorSearch and len(filtered_movies) > 0:
#    movies_dataframe = pd.DataFrame(filtered_movies)
#else:
#    movies_ref = list(dbMovies.stream())
#    movies_dict = [doc.to_dict() for doc in movies_ref]

##    movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
#    movies_dataframe = pd.DataFrame(movies_dict)
#
#if not movies_dataframe.empty:
#    st.dataframe(movies_dataframe, use_container_width=True)
#else:
#   st.write("No hay películas registradas")


#--------aqui voy
st.markdown("______________________________")
st.subheader("Listado de películas")

if not movies_df.empty:
    st.dataframe(movies_df, use_container_width=True)
else:
    st.write("No hay películas registradas")
