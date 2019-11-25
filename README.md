## Firbot

Firbot est un des bots du serveur privé Dur Dabla ; il remplit les fonctions suivantes :
* Envoi de messages programmés via [cron][1]
* Interface pour [cherchord][2] via la commande `!cherchord`
* Interface pour [timidity][3] via la commande `!play`

### Installation & lancement du bot

Firbot est écrit en Python 3.7 ; il peut être installé en entrant la ligne de commande suivante dans le répertoire
principal de Firbot (celui où se situe le fichier `setup.py`) :

```sh
python3.7 setup.py install
```

Avant de démarrer le bot, il faut passer son token d'authentification du bot dans la variable d'environnement
`FIRBOT_TOKEN`. Il peut ensuite être démarré via la ligne de commande suivante :

```sh
python3.7 firbot.py
```

### Tâches planifiées avec cron

Lors du démarrage, Firbot charge un fichier `cron.tab` depuis le sous-répertoire `firbot/data`. Ce fichier n'est pas
présent dans le dépôt GitHub pour des raisons de confidentialité. Chaque ligne correspond à la programmation d'un envoi
de message par le bot et doit respecter la syntaxe suivante :

```
cron-expression, channel-id, message
```

Exemple :

```
* * * * *, 000000000000000000, Le chantier avance :ok_hand:
```

### Interface pour cherchord

Firbot permet d'utiliser le programme en ligne de commande `cherchord` via la commande `!cherchord` s'il est installé
sur le serveur (voir la documentation de `cherchord` pour l'installation). Le fonctionnement étant globalement le même,
il est possible de se référer à la documentation d'origine pour les fonctionnalités de base.

Firbot supporte cependant quelques options supplémentaires par rapport au programme d'origine :
* Il est possible de lister les instruments disponibles via la commande `!cherchord --instruments`
* La commande `-i`/`--instrument` permet de spécifier un nombre de demi-tons à ajouter à chaque corde de l'instrument
  avant la recherche d'accords. Par exemple la commande `!cherchord Cmaj -i guitar/-2` permet de chercher des accords
  pour un instrument `guitar` dont toutes les cordes auraient été baissées d'un ton. Cette option peut également être
  utilisée pour chercher des accords avec un capodastre.

La liste des instruments disponibles est notamment plus grande que celle fournie par `cherchord` : elle est chargée
depuis le fichier de configuration `cherchord-config.json` du sous-répertoire `firbot/data`. Nous avons la main dessus
donc il est toujours possible de rajouter plus d'instruments sans avoir à modifier le projet d'origine.

### Interface pour timidity

Firbot permet également de lire des fichiers MIDI dans un canal vocal. Pour ce faire il faut d'abord constituer des
playlists dans le dossier ~/midi par exemple :
```
midi
├── playlist1
│   ├── song1.mid
│   └── song2.mid
└── playlist2
    ├── song3.mid
    └── song4.mid
```
Les commandes de recherche:
- Pour lister les playlists utiliser la commande `!playlists`
- Pour lister les morceaux la commande `!songs`
- Pour lister les morceaux d'une catégorie `!songs <nom playlist>`

Les commandes de contrôle:
- Pour lire un morceau: `!play <nom fichier> [options]...`
- Pour arrêter la lecture `!stop`

La commande `!play` accepte les options de timidity, pour les consulter: `man timidity`

  [1]: https://fr.wikipedia.org/wiki/Cron
  [2]: https://github.com/Aearnus/cherchord
  [3]: http://manpages.org/timidity
