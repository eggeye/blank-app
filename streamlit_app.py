import streamlit as st
import pandas as pd

# Titel
st.title("MätarHjälpen")

st.write("För oss som glömt notera mätarställningen 2")


# Val för visning i km eller mil
enhet = st.radio("Välj visningsenhet:", ["Kilometer (km)", "Mil"], index=1)

# Konverteringsfaktor för km till mil
km_to_mil = 0.1

# Dynamisk text baserad på val av enhet
enhet_text = "km" if enhet == "Kilometer (km)" else "mil"

# Input för senaste rapporterade mätarställning
senaste_matarstallning = st.number_input(
    f"Senaste rapporterad mätarställning ({enhet_text}):", min_value=1, step=10, value=None
)
datum_senaste_matarstallning = st.date_input(
    "Datum för senaste rapporterad mätarställning:", format="YYYY-MM-DD", value=None
)

# Mätarställning efter sista resan
matarstallning_efter = st.number_input(
    f"Mätarställning efter sista resan ({enhet_text}):", min_value=1, step=10, value=None
)

# Antal resor
antal_resor = st.number_input("Antal resor:", min_value=1, step=1, value=1)

# Dynamiska fält för resor baserat på antal_resor
st.write("### Resor")
resor = []
for resa in range(int(antal_resor)):
    st.write(f"#### Resa {resa + 1}")
    
    # Skapa kolumner för att placera fälten bredvid varandra
    col1, col2, col3 = st.columns([3, 3, 4])
    
    # Lägg in inputfält i respektive kolumn
    with col1:
        datum = st.date_input(
            f"Datum:", key=f"datum_{resa}", format="YYYY-MM-DD", value=None
        )
    with col3:
        destination = st.text_input(
            f"Destination:", key=f"destination_{resa}"
        )
    with col2:
        avstånd = st.number_input(
            f"Avstånd ({enhet_text}):", min_value=1, step=1, key=f"avstand_{resa}", value=None
        )
    
    # Lägg till resan i listan
    resor.append({"Datum": datum, "Destination": destination, "Avstånd": avstånd})


# Gör beräkningar när användaren klickar på "Beräkna"
if st.button("Beräkna"):
    # Skapa DataFrame
    df = pd.DataFrame(resor)

    # Kontrollera om alla fält är ifyllda
    if None in [senaste_matarstallning, matarstallning_efter] or df["Datum"].isnull().any() or any(df["Avstånd"] == 0):
        st.error("Vänligen fyll i alla fält korrekt.")
    else:
        # Omvandling till km om enheten är mil
        if enhet == "Mil":
            senaste_matarstallning *= 10
            matarstallning_efter *= 10
            df["Avstånd"] = df["Avstånd"] * 10

        # Sortera resor efter datum
        df["Datum"] = pd.to_datetime(df["Datum"])
        df = df.sort_values(by="Datum").reset_index(drop=True)

        # Beräkna antal dagar från senaste rapporterad mätarställning till första resa
        dagar_till_forsta_resa = (df["Datum"].iloc[0] - pd.to_datetime(datum_senaste_matarstallning)).days

        # Lägg till denna period som en "extra resa" i beräkningen
        df["Dagar"] = (df["Datum"].shift(-1) - df["Datum"]).dt.days.fillna(0).astype(int)
        total_dagar = dagar_till_forsta_resa + df["Dagar"].sum()

        # Beräkna differensen
        total_korstracka = matarstallning_efter - senaste_matarstallning
        summa_avstand = df["Avstånd"].sum()
        differens = total_korstracka - summa_avstand

        if differens < 0:
            st.error("Mätarställningen stämmer inte överens med de angivna avstånden!")
        else:
            # Fördela differensen proportionellt
            daglig_differens = differens / total_dagar if total_dagar > 0 else 0
            df["Differens"] = df["Dagar"] * daglig_differens

            # Inkludera dagarna från senaste rapporterad mätarställning
            extra_differens = dagar_till_forsta_resa * daglig_differens

            # Justera mätarställningar
            mätarresultat = []
            matarstallning_forr = senaste_matarstallning + extra_differens
            for i, row in df.iterrows():
                # Mätarställning efter = Mätarställning före + Avstånd
                matarstallning_efter = int(matarstallning_forr + row["Avstånd"])
                
                # Spara resultatet
                mätarresultat.append({
                    "Datum": row["Datum"].date(),
                    "Destination": row["Destination"],
                    "Avstånd": int(row["Avstånd"]),  # Visa som heltal
                    "Mätarställning Före": int(matarstallning_forr),  # Visa som heltal
                    "Mätarställning Efter": int(matarstallning_efter)  # Visa som heltal
                })
                
                # Uppdatera mätarställning före för nästa resa
                matarstallning_forr = matarstallning_efter + row["Differens"]

            # Skapa resultat DataFrame
            resultat_df = pd.DataFrame(mätarresultat)

            # Omvandling till mil om vald enhet är mil
            if enhet == "Mil":
                resultat_df["Avstånd (mil)"] = resultat_df["Avstånd"] * km_to_mil
                resultat_df["Mätarställning Före (mil)"] = resultat_df["Mätarställning Före"] * km_to_mil
                resultat_df["Mätarställning Efter (mil)"] = resultat_df["Mätarställning Efter"] * km_to_mil

                # Ta bort km-kolumner
                resultat_df.drop(columns=["Avstånd", "Mätarställning Före", "Mätarställning Efter"], inplace=True)

            # Anpassa format för att ta bort tusenavgränsare
            formatted_df = resultat_df.style.format(
                formatter={col: "{:.0f}".format for col in resultat_df.select_dtypes(include="number").columns}
            )

            # Visa resultatet
            st.write("### Resultat")
            st.dataframe(formatted_df)

            # Möjlighet att ladda ner resultatet som Excel-fil
            st.download_button(
                label="Ladda ner som Excel",
                data=resultat_df.to_csv(index=False).encode("utf-8"),
                file_name=f"Milkalkyl_{pd.Timestamp.now().date()}.csv",
                mime="text/csv"
            )
