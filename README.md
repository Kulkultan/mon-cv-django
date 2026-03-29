# MonCV Premium Diamant

Projet Django premium prêt à lancer.

## Inclus
- design ultra premium orienté recruteurs / LinkedIn / ATS
- cartes arrondies, ombres renforcées, typographie premium, impression PDF soignée
- titres d'expériences éditables dans l'admin
- dates de début / fin pour expériences et formations
- durée calculée automatiquement et affichée sur le CV
- expérience totale calculée automatiquement
- champs FR / EN manuels pour tous les éléments utiles
- mode clair / sombre
- sections masquées automatiquement lorsqu'elles sont vides

## Remarque
Les formulations des expériences et certains KPI sont des brouillons premium éditables, construits à partir des intitulés et organisations présents dans la base d'origine. Tu peux les affiner librement dans l'admin.

## Lancement
```bash
python -m venv venv
source venv/Scripts/activate   # Git Bash sous Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Mise en ligne
Le projet est prêt pour un hébergement type Railway ou Render.

### Variables d'environnement
Copier `.env.example` puis définir au minimum :
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL` si tu utilises PostgreSQL en production

### Commandes de déploiement
Build command :
```bash
./build.sh
```

Start command :
```bash
gunicorn MonCv.wsgi --log-file -
```

### Données du CV
Les données du CV peuvent être exportées puis réimportées :
```bash
python manage.py dumpdata cv --indent 2 --output cv/fixtures/cv_data.json
python manage.py loaddata cv/fixtures/cv_data.json
```
