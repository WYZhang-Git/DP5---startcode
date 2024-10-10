from pathlib import Path
import json
from database_wrapper import Database

def overzicht_attracties():
    # altijd verbinding openen om query's uit te voeren
    db.connect()

    select_query = """
    SELECT id, naam, type, attractie_min_lengte, attractie_max_lengte, attractie_min_leeftijd,
           attractie_max_gewicht, overdekt, geschatte_wachttijd, doorlooptijd, actief, productaanbod
    FROM voorziening
    WHERE type IN ('Achtbaan', 'Water', 'Draaien', 'Familie', 'Simulator', 'Horeca', 'Winkel');  
    """
    results = db.execute_query(select_query)

    # altijd verbinding sluiten met de database als je klaar bent
    db.close()

    return results

# maak zoals gewoonlijk connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark_software")

# navigeer naar het JSON-bestand, let op: er zijn ook andere persoonlijke voorkeuren om te testen! en maak vooral ook je eigen persoonlijke voorkeuren :-)
bestand_pad = Path(__file__).parent / 'persoonlijke_voorkeuren_bezoeker_1.json'

# open het JSON-bestand 
json_bestand = open(bestand_pad)
 
# zet het om naar een Python-dictionary
json_dict = json.load(json_bestand)

# nu kunnen we het gebruiken als een dict! dit is "dataset #1"
print(json_dict["naam"]) 

# en haal alle voorzieningen op, dit is een lijst met dicts. dit is "dataset #2"
list_met_voorzieningen = overzicht_attracties()
print(list_met_voorzieningen)

print("\n")
print(f"Dagplanner van: {json_dict['naam']} \n")

json_bestand.close() # sluit het bestand indien niet meer nodig

# DE OPDRACHT
# Met die 2 datasets moet je tot een persoonlijke programma komen voor de bezoeker
# Zorg dat je een algoritme ontwikkelt, conform eisen in het ontwerpdocument
# Zorg dat het persoonlijke programma genereert/output naar een .json bestand, dat weer ingelezen kan worden in een webomgeving (zie acceptatieomgeving website folder)
# Hieronder een begin...

# Initialiseer een lege lijst die de dagplanning zal bevatten

dagplanning = []

# Variabelen om de totale tijd van de dagplanning bij te houden
totale_tijd = 0
verblijfsduur = json_dict['verblijfsduur'] # Verblijfsduur van de bezoeker (in minunten)
horeca_moment_interval = 120  # Om de 2 uur wordt een horecagelegenheid toegevoegd 
laatste_horeca_moment = 0  # Houdt bij wanneer de laatste horecagelegenheid was toegevoegd

# Functie om te checken of een bezoeker aan de eisden voldoet van een voorziening
def toegankelijkheid_voorziening(voorziening, bezoeker):
    return (
        (voorziening['attractie_min_leeftijd'] is None or bezoeker['leeftijd'] >= voorziening['attractie_min_leeftijd']) and
        (voorziening['attractie_min_lengte'] is None or bezoeker['lengte'] >= voorziening['attractie_min_lengte']) and
        (voorziening['attractie_max_lengte'] is None or bezoeker['lengte'] <= voorziening['attractie_max_lengte']) and  
        (voorziening['attractie_max_gewicht'] is None or bezoeker['gewicht'] <= voorziening['attractie_max_gewicht'])
    )

def bereken_totale_geschatte_tijd(voorziening):
    return voorziening['geschatte_wachttijd'] + voorziening['doorlooptijd']

def voorkeur_eten_check(voorziening):
    voorkeuren = json_dict['voorkeuren_eten']
    
    return voorziening['productaanbod'].capitalize() in voorkeuren

# Functie om horecagelegenheid toe te voegen
def voeg_horecagelegenheid_toe(dagplanning, totale_tijd, laatste_horeca_moment):
    for voorziening in list_met_voorzieningen:
        if voorziening['type'] == 'horeca':
            if voorkeur_eten_check(voorziening) or not json_dict['voorkeuren_eten']:
                totale_geschatte_tijd_horeca = bereken_totale_geschatte_tijd(voorziening)
                if totale_tijd + totale_geschatte_tijd_horeca <= verblijfsduur:
                    dagplanning.append(voorziening)
                    totale_tijd += totale_geschatte_tijd_horeca
                    laatste_horeca_moment = totale_tijd
                    print(f"Horecagelegenheid toegevoegd: {voorziening['naam']}, totale tijd: {totale_tijd} minuten")  # Voor overzicht bij het testen
                    break  # Voeg alleen maar één horecagelegenheid toe aan de dagplanning
    return totale_tijd, laatste_horeca_moment
    
# Doorloop de lijst van voorzieningen en voeg attracties toe die aan de voorkeuren van de bezoeker voldoen
for voorziening in list_met_voorzieningen:       
    if voorziening['type'].capitalize() in json_dict['voorkeuren_attractietypes'] and toegankelijkheid_voorziening(voorziening, json_dict):
        totale_geschatte_tijd_attractie = bereken_totale_geschatte_tijd(voorziening)
    
        # Controleer of er genoeg tijd is
        if totale_tijd + totale_geschatte_tijd_attractie <= verblijfsduur:
            dagplanning.append(voorziening)  # Voeg attractie toe aan de dagplanning
            totale_tijd += totale_geschatte_tijd_attractie  # Tel de tijd op
            print(f"Toegevoegd: {voorziening['naam']}, totale tijd: {totale_tijd} minuten") # Voor overzicht bij het testen
        else:
            print(f"Niet genoeg tijd voor: {voorziening['naam']}")
            
 # Controleer of het tijd is om een horecagelegenheid toe te voegen
    if totale_tijd - laatste_horeca_moment >= horeca_moment_interval:
        totale_tijd, laatste_horeca_moment = voeg_horecagelegenheid_toe(dagplanning, totale_tijd, laatste_horeca_moment)
        
# Voeg een horecagelegenheid toe als de bezoeker langer dan 4 uur blijft
if verblijfsduur > 240 and totale_tijd - laatste_horeca_moment >= horeca_moment_interval:
    totale_tijd, laatste_horeca_moment = voeg_horecagelegenheid_toe(dagplanning, totale_tijd, laatste_horeca_moment)
            


 

# # Doorloop de lijst van voorzieningen (attracties) en voeg attracties toe die aan de voorkeuren van de klant voldoen

# for voorziening in list_met_voorzieningen:

#     # Controleer of het type van de attractie overeenkomt met de voorkeuren van de klant

#     # Let op: .capitalize() zorgt ervoor dat de vergelijking ongevoelig is voor hoofdletters/kleine letters

#     if voorziening['type'].capitalize() in json_dict['voorkeuren_attractietypes']:

#         # Print de naam en het type van de geselecteerde attractie voor testdoeleinden (debugging)

#         print(f"{voorziening['naam']} - {voorziening['type']}")

#         # Voeg de attractie toe aan de lijst van geselecteerde attracties

#         dagplanning.append(voorziening)

 

# # Genereer het dagprogramma voor de bezoeker

# # Dit programma bevat de naam van de bezoeker en een lijst van geselecteerde attracties op basis van zijn/haar voorkeuren

dagprogramma = {
    "voorkeuren": {
        "naam": json_dict["naam"],  # Naam van de bezoeker uit JSON  
        "gender": json_dict["gender"],  # Geslacht van de bezoeker uit JSON  
        "leeftijd": json_dict["leeftijd"], # Leeftijd van de bezoeker uit JSON  
        "lengte": json_dict["lengte"], # Lengte van de bezoeker uit JSON  
        "gewicht": json_dict["gewicht"], # Gewicht van de bezoeker uit JSON  
        "verblijfsduur": json_dict["verblijfsduur"], # Verblijfsduur van de bezoeker uit JSON  
        "voorkeuren_attractietypes": json_dict["voorkeuren_attractietypes"], # Voorkeuren attractietypes van de bezoeker uit JSON  
        "lievelings_attracties": json_dict["lievelings_attracties"], # Lieveling attracties van de bezoeker uit JSON  
        "rekening_houden_met_weer": json_dict["rekening_houden_met_weer"], # Rekening houden met het weer (ja/nee) uit JSON  
    },
    "voorzieningen": dagplanning  # Voeg de geselecteerde attracties en horeca toe aan het programma
}

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand
with open('persoonlijk_programma_bezoeker_x.json', 'w') as json_bestand:
    json.dump(dagprogramma, json_bestand, indent=4)

