import discord
import asyncio
import json
import schedule
from datetime import datetime, timedelta, timezone

# Remplace avec ton token sécurisé
TOKEN = ""
CHANNEL_ID =  # ID du canal où envoyer les messages du top10

def truncate_text(text, max_length=256):
    """Tronque le texte à max_length caractères en ajoutant '...' si nécessaire."""
    if len(text) > max_length:
        print(f"❌ Titre trop long avant troncature : {text}")
        return text[:max_length - 3] + "..."
    return text

# Charger les articles depuis le JSON
def fetch_articles_from_json():
    try:
        with open("published_articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
            print(f"✅ {len(articles)} articles chargés depuis le JSON.")
            return articles
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Erreur lors du chargement des articles : {e}")
        return []

# Récupérer les articles publiés cette semaine
def get_articles_of_the_week():
    articles = fetch_articles_from_json()
    
    today = datetime.utcnow().replace(tzinfo=timezone.utc)  
    start_of_week = today - timedelta(days=today.weekday())  

    weekly_articles = []
    for article in articles:
        try:
            pub_date = datetime.strptime(article["date_publication"], "%a, %d %b %Y %H:%M:%S %z")
            if pub_date >= start_of_week:
                weekly_articles.append(article)
        except ValueError:
            print(f"❌ Erreur de format de date pour l'article : {article['titre']}")
    
    print(f"📅 {len(weekly_articles)} articles trouvés pour cette semaine.")
    return weekly_articles

# Récupérer le top 10 des articles
def get_top_10_articles():
    weekly_articles = get_articles_of_the_week()
    sorted_articles = sorted(weekly_articles, key=lambda x: x["score"], reverse=True)
    return sorted_articles[:10]

# Publier le top 10 des articles
async def publish_top_10(client):
    """Envoie un embed Discord avec les 10 articles les plus populaires, avec plus de style."""
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ Impossible de trouver le canal Discord.")
        return

    async for message in channel.history(limit=10):
        if message.author == client.user:  # Vérifier si le message est envoyé par le bot
            await message.delete()  # Supprimer le message
            print("🗑️ Ancien message supprimé.")
            break  # Arrêter dès qu'on trouve le dernier message envoyé par le bot

    top_articles = get_top_10_articles()
    if not top_articles:
        await channel.send("🚨 Aucun article trouvé pour cette semaine.")
        return

    COLORS = [0xFFD700, 0xC0C0C0, 0xCD7F32]  # Or, Argent, Bronze
    DEFAULT_COLOR = 0x3498db  # Bleu par défaut
    EMOJIS = ["🏆","🥇", "🥈", "🥉"]
    
    embed = discord.Embed(
        title="✨ **Top 10 des articles de la semaine !** ✨",
        description="Voici les articles les plus populaires cette semaine 📅",
        color=0x1ABC9C,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text="📢 Veille Informatique | Mis à jour automatiquement")

    # Section "Top 3"
    embed.add_field(
        name="🏆 Top 3 Articles 📈",
        value="Voici les trois articles les plus populaires cette semaine!",
        inline=False
    )
    
    # Conversion de la date et formatage
    def format_date(date_str):
        if date_str != 'Date non disponible':
            try:
                timestamp = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                
                # Jours et mois en français
                jours = {
                    "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", 
                    "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", 
                    "Sunday": "Dimanche"
                }
                mois = {
                    "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", 
                    "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", 
                    "September": "Septembre", "October": "Octobre", "November": "Novembre", 
                    "December": "Décembre"
                }

                # Format de la date
                date_formatee = timestamp.strftime('%A %d %B %Y à %Hh%Mmin%S')
                date_formatee = date_formatee.replace(timestamp.strftime('%A'), jours[timestamp.strftime('%A')])\
                                            .replace(timestamp.strftime('%B'), mois[timestamp.strftime('%B')])
                return date_formatee
            except ValueError:
                return "Date non disponible"
        return 'Date non disponible'


    # Code principal
    for i, article in enumerate(top_articles[:3], start=1):  # Limité aux 3 premiers articles
        emoji = EMOJIS[i] if i < len(EMOJIS) else "🔹"
        color = COLORS[i - 1] if i <= 3 else DEFAULT_COLOR

        title = article['titre']
        truncated_title = truncate_text(title)  # Appliquer la troncature

        score = f"📊 **Score** : `{article['score']}`"
        date_pub = f"📰 **Publié le** {format_date(article['date_publication'])}"  # Applique le formatage de la date
        
        field_name = f"{emoji} {truncated_title}"
        
        if len(field_name) > 256:
            field_name = truncate_text(field_name)  # Tronquer à 256 si nécessaire

        field_value = f"[🔗 Lien]({article['lien']})\n{score} | {date_pub}"

        embed.add_field(
            name=field_name,
            value=field_value,
            inline=False
        )

    
    # Section "Autres articles"
    embed.add_field(
        name="🔹 Autres articles intéressants",
        value="Voici d'autres articles que vous pourriez trouver intéressants!",
        inline=False
    )

    # Ajouter les autres articles (de la 4e à la 10e position)
    for i, article in enumerate(top_articles[3:10], start=4):  # Limité aux articles de 4 à 9
        emoji = EMOJIS[i] if i < len(EMOJIS) else "🔹"
        
        title = article['titre']
        truncated_title = truncate_text(title)

        score = f"📊 **Score** : `{article['score']}`"
        date_pub = f"📰 **Publié le** {format_date(article['date_publication'])}"  # Applique le formatage de la date
        
        field_name = f"{emoji} [{truncated_title}]"
        
        if len(field_name) > 256:
            field_name = truncate_text(field_name)

        field_value = f"[🔗 Lien]({article['lien']})\n{score} | {date_pub}"

        embed.add_field(
            name=field_name,
            value=field_value,
            inline=False
        )

    await channel.send(embed=embed)
    print("✅ Top 10 envoyé avec succès !")


async def run_top10(client):
    await publish_top_10(client)
