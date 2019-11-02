### Firbot

Pour le moment c'est un bot en Python d'une simplicité naïve. Pour l'utiliser il faut :
* Un Python 3 récent
* Le module crontab
* Le module discord.py
* Le module chatterbot
* Le module chatterbot_corpus

Pour fonctionner, le script a besoin que le token d'authentification du bot soit passé dans
la variable d'environnement `FIRBOT_TOKEN`. Il chargera alors un fichier `cron.tab` dans son
répertoire avec la syntaxe suivante :

```
cron-expression, channel-id, message
```

Exemple :

```
* * * * *, 000000000000000000, Le chantier avance :ok_hand:
```

Il est possible de lui apprendre des dialogues avec la commande ``!learn``
Exemple:
```
!learn "phrase 1" "phrase 2" "phrase 3"
```
