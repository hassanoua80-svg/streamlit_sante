# Dashboard Streamlit – Organisation des rendez-vous de soins

Projet de Data Analytics réalisé avec **pandas**, **matplotlib** et **Streamlit**.

## Contenu

- `app.py` : application Streamlit
- `requirements.txt` : bibliothèques nécessaires
- `rendez_vous_soins_2026.xlsx` : jeu de données Excel utilisé par l'application
- `README.md` : documentation du projet

## Jeu de données

Le fichier pédagogique décrit **800 rendez-vous fictifs** entre janvier et août 2026.

Colonnes principales :

- ID rendez-vous
- Date rendez-vous
- Ville
- Service
- Canal réservation
- Type visite
- Délai RDV (jours)
- Statut
- Attente sur place (min)
- Consultation (min)
- Satisfaction /5

Les champs d'attente, de consultation et de satisfaction sont vides lorsque le rendez-vous n'est pas honoré. Ils sont donc traités comme des valeurs manquantes et non comme des zéros.

## Questions traitées

1. Service recevant le plus de rendez-vous
2. Taux d'honorés, absents et annulés par service
3. Services avec les délais de rendez-vous les plus longs
4. Variation de l'attente moyenne selon la ville pour les visites honorées
5. Évolution mensuelle du volume et des absences
6. Proposition d'amélioration organisationnelle basée sur les chiffres

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publier sur Streamlit Community Cloud

1. Créer un dépôt public ou privé sur GitHub.
2. Ajouter `app.py`, `requirements.txt`, `README.md` et `rendez_vous_soins_2026.xlsx` à la racine du dépôt.
3. Ouvrir Streamlit Community Cloud.
4. Choisir **Create app** puis sélectionner le dépôt GitHub.
5. Indiquer `app.py` comme fichier principal.
6. Déployer l'application.
7. Copier le lien public obtenu et le remettre dans Classroom.

## Conclusion personnelle proposée

Ce projet m'a permis d'utiliser pandas pour nettoyer et analyser des données de rendez-vous et matplotlib pour visualiser les résultats. J'ai découvert que le volume des rendez-vous est particulièrement important en médecine générale, tandis que la cardiologie présente le délai moyen de rendez-vous le plus long. J'ai aussi observé des différences d'attente selon les villes et une hausse marquée des absences en mars. Je recommande de renforcer les rappels et la confirmation des rendez-vous, en particulier pour les réservations via le site web, puis de suivre l'évolution du taux d'absence après cette action.

## Limites

Les données sont fictives et administratives. Les différences observées entre services, villes ou canaux sont descriptives : elles ne permettent pas, à elles seules, de conclure à une relation de cause à effet.
