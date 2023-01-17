# Utilitaire de deplacement de fichiers/dossiers en python

Cet utilitaire permet de déplacer tous les fichier présents dans le dossier **src** vers le dossier **dest** en verifiant à interval de **t**s que la taille des fichiers/dossiers n'a pas changé. Cela permet d'éviter le problème du deplacement de fichier lors d'une copie.

## Utilisation

```shell
# installation

# 1) Installer Python depuis le gestionnaire d'application

# 2) Creer une "Tache planifie" a executer une seul fois:
python3 -m pip install -U watchdog;
wget -O moving_script.py https://raw.githubusercontent.com/misteriaud/imagine_moving_script/master/watch_dog.py

# 3) Creer pour chacuns des dossier a synchroniser la "Tache declenche" -> "Script definie par l'utilisateur":
python3 /root/moving_script.py "dossier_source" "dossier_destination" 120
```
