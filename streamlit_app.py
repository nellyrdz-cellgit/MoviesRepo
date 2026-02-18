import pandas as pd
import numpy as np
import streamlit as st

from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-project")
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

#Busca por nombre
def loadByName(name):
  movies_ref = dbMovies.where(u'name', u'==', name)
  currentName = None
  for myname in movies_ref.stream():
    currentName = myname
  return currentName

st.sidebar.subheader("Buscar nombre de película")
nameSearch = st.sidebar.text_input("Nombre")
btnFiltrar = st.sidebar.button("Filtrar")

if (btnFiltrar):
  doc = loadByName(nameSearch)
  if doc is None:
    st.sidebar.write("La película no existe en nuestra base de datos")
  else:
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


#Listado de peliculas
movies_ref = list(db.collection(u'movies').stream())
movies_dict = list(map(lambda x: x.to_dict(), movies_ref))
movies_dataframe = pd.DataFrame(movies_dict)
st.dataframe(movies_dataframe)

