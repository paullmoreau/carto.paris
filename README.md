# Carto

Carte interactive des lieux pour jouer aux jeux de bistrot autour de toi : billard, fléchettes, baby-foot, flipper, beer-pong, jeux de société, échecs, pétanque, ping-pong, karaoké, quiz, arcade, bowling…

Site : https://paullmoreau.github.io/carto.paris/

- Position en temps réel et filtres par jeu
- Lieux OpenStreetMap (Overpass) + sélection parisienne dans `places.json`
- Favoris, liste façon dossiers Apple, marqueurs emoji avec nom
- « Ouvert maintenant » d'après les horaires OpenStreetMap ou ceux de `places.json`
- Soirées récurrentes (quiz, karaoké, jams, tournois…) dans `events.json`, plus celles que l'utilisateur ajoute
- Bouton « Ajouter un lieu » (enregistré sur l’ppareil, option de proposition à OpenStreetMap)

Pour ajouter un lieu à la sélection pour tout le monde : ajoute une entrée dans `places.json` (nom, adresse, jeux, source).

## Carte

Interface claire façon iOS / Bump / Snap Map. Fond de carte façon Google Maps (`map-style.json` et `map-style-dark.json`, générés par `tools/googlestyle.py` à partir du style Liberty) sur les tuiles gratuites [OpenFreeMap](https://openfreemap.org), affiché avec MapLibre. Pour changer les couleurs : modifier le dictionnaire `P` dans `tools/genstyle.py` puis régénérer le style. Si le téléphone ne gère pas WebGL, la carte bascule automatiquement sur CARTO Positron.

Données © OpenStreetMap, © OpenMapTiles, géocodage Géoplateforme IGN.

## Base de données partagée (Supabase)

Les lieux et soirées ajoutés depuis l'app sont enregistrés dans Supabase et visibles par tous.

1. Créer un projet gratuit sur https://supabase.com
2. SQL Editor > New query : coller `supabase-setup.sql`, remplacer `TON-MOT-DE-PASSE` par le mot de passe admin, puis Run
3. Project Settings > API : copier l'URL du projet et la clé « anon public » dans `config.js`

Le bouton ✏️ d'un lieu permet à l'admin de corriger les jeux, les horaires, le nom, ou de masquer le lieu.
Le mot de passe est vérifié par Supabase et n'apparaît jamais dans le code.
