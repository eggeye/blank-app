import streamlit as st
# Titel
st.title("MätarHjälpen")
st.write("För oss som glömt notera mätarställningen")
# Antal resor - Hämta värdet
antal_resor = st.number_input("Antal resor:", min_value=1, step=1, value=1)
matarstallning_innan = st.number_input("Mätarställning (km) innan första resan:", min_value=1,step=10,  value=None)
matarstallning_efter = st.number_input("Mätarställning (km) efter sista resan:", min_value=1, step=10, value=None)
# Dynamiska fält för resor baserat på antal_resor
st.write("### Resor")
for resa in range(int(antal_resor)):
    st.write(f"#### Resa {resa + 1}")
    datum = st.date_input(f"Datum för resa {resa + 1}", key=f"datum_{resa}", format="YYYY-MM-DD", value=None)
    destination = st.text_input(f"Destination för resa {resa + 1}", key=f"destination_{resa}")
    avstånd = st.number_input(f"Avstånd (km) för resa {resa + 1}", min_value=0, step=10, key=f"avstand_{resa}")
