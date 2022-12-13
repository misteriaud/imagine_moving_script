# Utilitaire de deplacement de fichiers/dossiers en python

Cet utilitaire permet de déplacer tous les fichier présents dans le dossier **src** vers le dossier **dest** en verifiant à interval de **t**s que la taille des fichiers/dossiers n'a pas changé. Cela permet d'éviter le problème du deplacement de fichier lors d'une copie.

## Utilisation

```shell
# installation
git clone https://github.com/misteriaud/imagine_moving_script.git moving_script
cd moving_script

# lancement
python moving_script.py "src_folder" "dest_foler" 5 || /usr/local/bin/python3 moving_script.py "src_folder" "dest_foler" 5
```
