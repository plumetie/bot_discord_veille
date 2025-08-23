import json
import locale
import feedparser
import discord
from bs4 import BeautifulSoup
from datetime import datetime
from top10 import run_top10
import os
import asyncio

URLS_RSS = [
    "https://www.undernews.fr/feed",
    "https://krebsonsecurity.com/feed/",
    "https://cert.ssi.gouv.fr/feed/",
    "https://www.exploitone.com/feed/", 
    "https://heimdalsecurity.com/blog/feed/",
    "https://www.grahamcluley.com/feed/",
    "https://hackercombat.com/feed/",
    "https://securelist.com/feed/",
    "https://www.tripwire.com/state-of-security/feed/",
    "https://www.zataz.com/feed/"
]

MOTS_CLES = {
    "cybersécurité": 3,
    "ransomware": 5,
    "faille": 4,
    "piratage": 5,
    "hacking": 4,
    "malware": 5,
    "phishing": 5,
    "exploitation": 4,
    "vulnérabilité": 4,
    "attaque": 4,
    "exploit": 6,
    "sécurité informatique": 3,
    "cryptage": 2,
    "fraude informatique": 5,
    "botnet": 6,
    "zero-day": 6,
    "attaque DDoS": 5,
    "ingénierie sociale": 5,
    "trojan": 5,
    "cheval de Troie": 5,
    "maliciel": 5,
    "cryptomining": 4,
    "ransomware-as-a-service": 6,
    "zéro-day": 6,
    "botnet": 6,
    "DNS hijacking": 5,
    "cryptojacking": 5,
    "virus informatique": 5,
    "attaque par force brute": 4,
    "escalade de privilèges": 5,
    "attaque par injection SQL": 5,
    "XSS": 5,
    "attaque par phishing": 5,
    "exploit kit": 6,
    "attaque sur le cloud": 5,
    "data breach": 6,
    "exfiltration de données": 5,
    "vol de données": 5,
    "fuite de données": 5,
    "sécurisation": 4,
    "authentification multi-facteurs": 4,
    "MFA": 4,
    "clés API": 3,
    "securisation des réseaux": 4,
    "firewall": 3,
    "VPN": 3,
    "chiffrement": 4,
    "certificat SSL": 3,
    "protection antivirus": 3,
    "mise à jour logicielle": 4,
    "patching": 4,
    "brute force": 5,
    "social engineering": 5,
    "attacks on endpoints": 5,
    "rootkit": 6,
    "backdoor": 5,
    "APT": 6,
    "spear phishing": 5,
    "worm": 5,
    "botnet": 6,
    "spoofing": 5,
    "DDoS": 5,
    "web shell": 6,
    "man-in-the-middle": 5,
    "bypass de sécurité": 5,
    "téléchargement de logiciels malveillants": 5,
    "propagation de malware": 5,
    "coupure de service": 5,
    "attaque de type MITM": 5,
    "falsification de requêtes": 4,
    "téléchargement automatique": 5,
    "surveillance réseau": 4,
    "hygiène numérique": 4,
    "sécurisation des données": 5,
    "protection des données personnelles": 5,
    "respect de la vie privée": 5,
    "encryption": 4,
    "exploitation des failles": 6,
    "attaque par injection de commande": 6,
    "récupération de mots de passe": 4,
    "les attaques Wi-Fi": 5,
    "cyberattaque": 5,
    "privilèges d'administration": 4,
    "intrusion réseau": 5,
    "vol d'identifiants": 5,
    "compromission de compte": 5,
    "cybercriminalité": 5,
    "cyberespionnage": 6,
    "surveillance en ligne": 3,
    "hameçonnage": 5,
    "ransomware locker": 6,
    "sécurisation des applications": 4,
    "cryptographie symétrique": 4,
    "cryptographie asymétrique": 4,
    "attachement malveillant": 5,
    "rooter": 6,
    "malware-as-a-service": 5,
    "menace interne": 5,
    "sécurité mobile": 4,
    "système d'authentification": 4,
    "protection contre les ransomwares": 5,
    "détection d'intrusion": 4,
    "logs de sécurité": 4,
    "sensibilisation à la sécurité": 3,
    "VPN pour sécurité": 4,
    "analyse de la vulnérabilité": 4,
    "protection anti-malware": 4,
    "mises à jour de sécurité": 4,
    "réponse aux incidents de sécurité": 5,
    "services de renseignement sur les menaces": 4,
    "sécurité des applications web": 5,
    "authentification forte": 4,
    "protection contre les attaques DDoS": 5,
    "cyber-assurance": 4,
    "techniques de piratage": 5,
    "identité numérique": 4
}

PUBLISHED_ARTICLES_FILE = 'published_articles.json'

if not os.path.exists(PUBLISHED_ARTICLES_FILE):
    print(f"Le fichier {PUBLISHED_ARTICLES_FILE} n'existe pas. Création d'un fichier avec une liste vide.")
    with open(PUBLISHED_ARTICLES_FILE, 'w') as file:
        json.dump([], file) 
else:
    print(f"Le fichier {PUBLISHED_ARTICLES_FILE} existe déjà.")

def load_published_articles():
    try:
        with open(PUBLISHED_ARTICLES_FILE, 'r') as f:
            articles = json.load(f)
            print("Articles déjà publiés chargés.")
            return articles
    except Exception as e:
        print(f"Erreur lors du chargement des articles : {e}")
        return []


def save_published_articles(published_articles):
    try:
       
        directory = os.path.dirname(PUBLISHED_ARTICLES_FILE)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)  

        with open(PUBLISHED_ARTICLES_FILE, 'w') as f:
            json.dump(published_articles, f, indent=4)
        print("Articles publiés sauvegardés avec succès.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des articles dans {PUBLISHED_ARTICLES_FILE}: {e}")



def nettoyer_description(description):
    soup = BeautifulSoup(description, "html.parser")
    return soup.get_text()

def pertinence(article, mots_cles):
    score = 0
    article_text = article['titre'] + " " + article['description']
    for mot, poids in mots_cles.items():
        score += article_text.lower().count(mot.lower()) * poids
    return score


def recuperer_articles(url_rss):
    flux = feedparser.parse(url_rss)
    articles = []

    for entry in flux.entries:
        titre = entry.title
        description = entry.get("description", "")
        lien = entry.link
        id_article = entry.id  
        date_publication = entry.get("published", "Date non disponible")
        auteur = entry.get("author", "Auteur non disponible")

        description_nettoyee = nettoyer_description(description)

        article_data = {
            "id": id_article,
            "titre": titre,
            "description": description_nettoyee,
            "lien": lien,
            "score": pertinence({"titre": titre, "description": description_nettoyee}, MOTS_CLES),
            "date_publication": date_publication,
            "auteur": auteur
        }

        articles.append(article_data)
    
    articles = sorted(articles, key=lambda x: x["score"], reverse=True)
    return articles

async def envoyer_articles(client, channel):
    published_articles = load_published_articles()
    print(f"Articles publiés avant ajout : {published_articles}")
    articles_nouveaux = []

    for url_rss in URLS_RSS:
        articles = recuperer_articles(url_rss)

        for article in articles:
            if article["score"] <= 10:
                print(f"Article filtré : {article['titre']} (score trop faible)")
                continue 

            if article["id"] not in [a["id"] for a in published_articles]:  
                articles_nouveaux.append(article)
                published_articles.append(article)  
                print(f"Nouvel article ajouté : {article['titre']}")
            else :
                print(f"Article déjà publié : {article['titre']}")

    for article in articles_nouveaux:
        color = discord.Color.green() if article['score'] > 30 else discord.Color.orange() if article['score'] > 15 else discord.Color.red()

        if article['date_publication'] != 'Date non disponible':
            timestamp = datetime.strptime(article['date_publication'], '%a, %d %b %Y %H:%M:%S %z')
            
            date_formatee = timestamp.strftime('%A %d %B %Y à %Hh%Mmin%S')
            jours = {
                "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"
            }
            mois = {
                "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", 
                "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"
            }
            
            date_formatee = date_formatee.replace(timestamp.strftime('%A'), jours[timestamp.strftime('%A')]).replace(timestamp.strftime('%B'), mois[timestamp.strftime('%B')])

        else:
            timestamp = None 
            date_formatee = 'Date non disponible'

        embed = discord.Embed(
            title=f"🚨 {article['titre']}",
            description=f"{article['description'][:250]}...",  
            url=article['lien'],
            color=color,
            timestamp=timestamp  
        )

        embed.add_field(name="🖊️ Auteur", value=article['auteur'], inline=True)
        embed.add_field(name="📅 Date de publication", value=date_formatee, inline=True)  
        embed.add_field(name="🔎 Pertinence", value=f"Score: {article['score']}", inline=True)

        if "ransomware" in article['titre'].lower():
            embed.set_image(url="https://drive.google.com/uc?export=view&id=1ILh2p1AcS165T7hDuROkM6UQtRVUCI5C")
        elif "malware" in article['titre'].lower():
            embed.set_image(url="https://drive.google.com/uc?export=view&id=1BU8q9PA7dHnN8KYSsx_NP9YLySbl-Dtj")
        elif "phishing" in article['titre'].lower():
            embed.set_image(url="https://drive.google.com/uc?export=view&id=1RQ09biGzr8HodbNq29YRyW8L3COs3MsK")
        elif "ddos" in article['titre'].lower():
            embed.set_image(url="https://drive.google.com/uc?export=view&id=1du6AOQcDkQLuxrWYyuGE2NyCE1b0UZ0Q")

        message = await channel.send(embed=embed)
        await message.add_reaction('👍')  
        await message.add_reaction('👎')

    if articles_nouveaux == [] :
      ##
      # ID du channel pour publier les articles quotidien
      ##
            channel = client.get_channel('''Placez votre ID ici''')
            await channel.send("Aucun articles aujourd'hui 📰")

    print(f"Articles publiés après ajout : {published_articles}")
    save_published_articles(published_articles)

intents = discord.Intents.default()
intents.message_content = True  
client = discord.Client(intents=intents)

async def boucle_quotidienne():
    await client.wait_until_ready()
    channel = client.get_channel(1353362540767219804)
    if not channel:
        print("Canal introuvable!")
        return
    while not client.is_closed():
        await envoyer_articles(client, channel)
        print("Début de l'attente")
        await asyncio.sleep(120)  # attendre 2 min
        print("Attente terminée, exécution de run_top10...")
        try:
            await run_top10(client)
        except Exception as e:
            print(f"Erreur dans run_top10 : {e}")
        await asyncio.sleep(86400 - 120)  # compléter 24h

@client.event
async def on_ready():
    print(f'Bot connecté en tant que {client.user}')
    asyncio.create_task(boucle_quotidienne()) 

@client.event
async def on_message(message):
    # Empêche le bot de répondre à lui-même
    if message.author == client.user:
        return

    # Si le message est "!top10", exécute la fonction
    if message.content.strip() == "!top10":
        await message.channel.send("📊 Génération du top 10 en cours...")
        try:
            await run_top10(client)
            await message.channel.send("✅ Top 10 généré avec succès.")
        except Exception as e:
            await message.channel.send(f"❌ Erreur lors de la génération du top 10 : {e}")
            print(f"Erreur dans !top10 : {e}")

# Token Discord
client.run('Placez votre token ici !')
