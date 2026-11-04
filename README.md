# Tournée Générale

Carte interactive des lieux pour jouer aux jeux de bistrot autour de toi : billard, fléchettes, baby-foot, flipper, beer-pong, jeux de société, échecs, pétanque, ping-pong, karaoké, quiz, arcade, bowling…

Site : https://paullmoreau.github.io/carto.paris/

- Position en temps réel et filtres par jeu
- Lieux OpenStreetMap (Overpass) + sélection parisienne dans `places.json`
- Favoris, liste façon dossiers Apple, marqueurs emoji avec nom
- Bouton « Ajouter un lieu » (enregistré sur l’ppareil, option de proposition à OpenStreetMap)

Pour ajouter un lieu à la sélection pour tout le monde : ajoute une entrée dans `places.json` (nom, adresse, jeux, source).

## Carte

Interface claire façon iOS / Bump / Snap Map. Fond de carte vectoriel maison « Tournée » (palette « bump ») (`map-style.json`) sur les tuiles gratuites [OpenFreeMap](https://openfreemap.org), affiché avec MapLibre. Pour changer les couleurs : modifier le dictionnaire `P` dans `tools/genstyle.py` puis régénérer le style. Si le téléphone ne gère pas WebGL, la carte bascule automatiquement sur CARTO Positron.

Données © OpenStreetMap, © OpenMapTiles, géocodage Géoplateforme IGN.
