# 🤖 Discord News Bot

Un bot **Discord** en Python permettant de recenser chaque jour des articles dans un salon dédié, filtrés selon une **liste de mots-clés**.  
Chaque article est analysé, reçoit un **score** basé sur le nombre de mots-clés détectés, et est publié dans un salon d’actualités.  

En fin de semaine, un **Top 10 des articles** les plus pertinents est généré dans un second salon.  
Idéal pour faire de la veille informatique automatisée sur un serveur Discord.

---

## ✨ Fonctionnalités

- 📡 **Récupération d’articles** à partir de flux RSS configurés  
- 📝 **Filtrage par mots-clés** (ex: *cyberattaque, phishing, pare-feu…*)  
- ⚡ Attribution d’un **score** à chaque article selon :  
  - nombre de mots-clés trouvés  
  - pondération selon l’importance du mot-clé  
- 📌 Publication automatique dans un **salon Discord d’actualités**  
- 🏆 Génération d’un **Top 10 hebdomadaire** dans un autre salon  
- 🎨 Liens présentés avec titre, année, résumé et lien vers l’article  

---

## 🛠️ Installation

### 1. Cloner le projet
```bash
git clone https://github.com/ton-compte/discord-news-bot.git
cd discord-news-bot
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

La configuration se fait **directement dans les fichiers Python** :

- 🔑 **Token Discord**  
  Dans `bot.py`, à la fin du fichier :  
  ```python
  client.run("TON_TOKEN_DISCORD")
  ```

- 📝 **Salon d’actualités (quotidien)**  
  Dans `bot.py`, la fonction :  
  ```python
  async def boucle_quotidienne():
      await client.wait_until_ready()
      channel = client.get_channel(ID_DU_CHANNEL_ICI)
  ```

- 🏆 **Salon du Top 10 hebdomadaire**  
  Dans `top10.py`, la variable :  
  ```python
  CHANNEL_ID = ID_DU_CHANNEL_ICI
  ```

- 🔎 **Mots-clés et pondérations**  
  Dans `bot.py`, la liste est définie directement en Python, par exemple :  
  ```python
  keywords = {
      "cyberattaque": 5,
      "phishing": 4,
      "vpn": 3,
      "pare-feu": 2,
      "ransomware": 5
  }
  ```

---

## ▶️ Lancer le bot

Exécuter simplement le script principal :

```bash
python bot.py
```

Pour lancer le classement hebdomadaire :

```bash
python top10.py
```

---

## 🔎 Fonctionnement

1. Le bot collecte les articles depuis les flux RSS définis.  
2. Analyse le contenu : recherche de mots-clés dans le titre et la description.  
3. Calcule un score basé sur les mots trouvés.  

   Exemple →  

   - Article : "Nouvelle cyberattaque exploitant une faille VPN"  
   - Mots-clés trouvés : cyberattaque (5 pts) + vpn (3 pts)  
   - Score final = 8 pts  

4. Publie dans Discord avec format clair :  

```text
[2025] 🔹 X victime d’une attaque DDoS
🔗 Lire l’article : https://...
Score : 8 pts
```

5. Génère un **Top 10** hebdomadaire :  

```text
🏆 Top 10 des articles de la semaine :
1️⃣ [2025] Cyberattaque majeure... (12 pts)
2️⃣ [2024] Phishing Astaroth... (10 pts)
...
```

---

## 🚀 Améliorations futures

- Commandes Discord `/config` pour changer les mots-clés et salons  
- Export automatique du Top 10 en `.pdf` ou `.md`  
- Dashboard web pour gérer les mots-clés et l’historique  

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Forkez le projet  
2. Créez une branche (feature/ma-fonctionnalite)  
3. Faites une Pull Request  

---

## 📄 Licence

Ce projet est sous licence MIT.  
Libre à vous de l’utiliser et de l’adapter à vos besoins.
