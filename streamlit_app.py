import pandas as pd
import numpy as np
import streamlit as st

from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies")
dbMovies = db.collection('movies')

# Titulo
st.title("Lista de Películas")


# Crea película
st.header("Nueva película")
name = st.text_input('Nombre de la película: ')
filemcompany = st.text_input('Compañía Cinematográfica: ')
director = st.text_input('Director: ')
genre = st.text_input('Género: ')

submit = st.button('Crear nueva película')

if name and filemcompany and director and genre and submit:
  doc_ref = db.collection('movies').document(name)
  doc_ref.set({
      'name':name,
      'filemcompany':filemcompany,
      'director':director,
      'genre':genre
  })
  st.sidebar.write('Película agregada')

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

if btnFiltrar and DirectorSearch:
    docs = loadByDirector(DirectorSearch)

    if len(docs) == 0:
        st.sidebar.write("No existen películas del director en la base de datos")
    else:
        st.sidebar.write(f"Películas de {DirectorSearch}:")
        for doc in docs:
            st.sidebar.write(doc.to_dict())


#Eliminar
st.sidebar.markdown("---'")
btnEliminar = st.sidebar.button("Eliminar")

if (btnEliminar):
  deletename = loadByName(nameSearch)
  if deletename is None:
    st.sidebar.write("La película no existe en nuestra base de datos")
  else:
    dbMovies.document(deletename.id).delete()
    st.sidebar.write("Película eliminada")

st.sidebar.markdown("---'")

#Modificar
newname = st.sidebar.text_input("Modificar nombre")
btnModificar = st.sidebar.button("Modificar")

if btnModificar:
  updatename = loadByName(nameSearch)
  if updatename is None:
    st.sidebar.write("La película no existe en nuestra base de datos")
  else:
    myupdatename=dbMovies.document(updatename.id)
    myupdatename.update({
        'name': newname
    })


# Listado  de películas
st.markdown("---")
st.subheader("Listado completo de películas")

movies_ref = list(dbMovies.stream())
movies_dict = list(map(lambda x: x.to_dict(), movies_ref))

if len(movies_dict) > 0:
    movies_dataframe = pd.DataFrame(movies_dict)
    st.dataframe(movies_dataframe)
else:
    st.write("No hay películas registradas")

