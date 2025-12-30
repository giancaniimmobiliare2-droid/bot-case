import pandas as pd
import os

# --- LINK CONVERTITI CORRETTAMENTE IN CSV ---
# Questi sono i TUOI fogli, ma formattati per Python
URL_ACQUIRENTI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=1947365306&single=true&output=csv"
URL_IMMOBILI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=835643388&single=true&output=csv"

OUTPUT_DIR = "pagine_clienti"

# --- 1. PREPARAZIONE ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("Scaricamento dati in corso...")

try:
    df_immobili = pd.read_csv(URL_IMMOBILI)
    df_acquirenti = pd.read_csv(URL_ACQUIRENTI)
    print("✅ Dati scaricati! Colonne trovate:")
    print(f"Immobili: {list(df_immobili.columns)}")
    print(f"Acquirenti: {list(df_acquirenti.columns)}")

    # Pulizia Prezzi e Budget (toglie simbolo € e spazi)
    # Rinomina colonne per sicurezza (in minuscolo) se serve, ma proviamo diretto
    df_immobili['prezzo'] = pd.to_numeric(df_immobili['prezzo'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    df_acquirenti['Budget Max'] = pd.to_numeric(df_acquirenti['Budget Max'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')

except Exception as e:
    print(f"❌ ERRORE LETTURA DATI: {e}")
    exit()

# --- 2. TEMPLATE HTML ---
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Proposte Immobiliari</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; background: #f0f2f5; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .price {{ color: green; font-weight: bold; font-size: 1.2em; }}
        .btn {{ background: #007bff; color: white; padding: 10px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;}}
    </style>
</head>
<body>
    <h1>Ciao {nome}, ecco cosa ho trovato a {citta}:</h1>
    {contenuto}
</body>
</html>
"""

# --- 3. GENERAZIONE PAGINE ---
count = 0
print("Inizio Matching...")

for index, cliente in df_acquirenti.iterrows():
    nome = str(cliente['Nome'])
    citta_cliente = str(cliente['Città'])
    budget = cliente['Budget Max']
    
    # FILTRO: Zona contiene Città cliente E Prezzo <= Budget
    match = df_immobili[
        (df_immobili['zona'].str.contains(citta_cliente, case=False, na=False)) & 
        (df_immobili['prezzo'] <= budget)
    ]
    
    if not match.empty:
        schede = ""
        for idx, casa in match.iterrows():
            schede += f"""
            <div class="card">
                <h3>{casa['zona']} - {casa['camere']} Camere</h3>
                <p>{casa['descrizione']}</p>
                <p class="price">€ {casa['prezzo']}</p>
                <a href="{casa['foto_url']}" class="btn">Vedi Foto</a>
            </div>
            """
        
        pagina = html_template.format(nome=nome, citta=citta_cliente, contenuto=schede)
        
        # Salva file
        clean_name = nome.replace(" ", "_")
        filename = f"proposte_{cliente['id']}_{clean_name}.html"
        
        with open(f"{OUTPUT_DIR}/{filename}", "w") as f:
            f.write(pagina)
            
        print(f"✅ Generata pagina per: {nome}")
        count += 1

if count == 0:
    print("⚠️ Nessuna pagina generata. Nessuna casa corrisponde alle richieste (Controlla che i prezzi siano numeri!).")
