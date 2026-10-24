# Soumission Radar

Site statique de veille des appels d'offres publics au Québec.

## Installation

Téléverser les **fichiers extraits**, en conservant les dossiers `.github/workflows` et `scripts`, à la racine du dépôt GitHub. Ne pas téléverser seulement l'archive ZIP.

## Automatisation

Le workflow GitHub Actions `Actualiser les appels d'offres SEAO` tente une importation quotidienne des ressources JSON hebdomadaires de Données Québec. Le parseur est volontairement prudent : en cas de changement de schéma, il échoue sans publier de données inventées. **Il doit être validé sur une exécution réelle** avant de considérer la synchronisation comme opérationnelle. Les données initiales sont vides.

## Publication

Créer un projet Cloudflare Pages connecté à ce dépôt GitHub, avec répertoire de sortie `.` et sans commande de build. Un projet Pages créé initialement en *Direct Upload* peut nécessiter la création d'un nouveau projet pour la connexion Git.

## Contact

Le bouton de formulaire est un emplacement réservé non opérationnel. Configurer un véritable formulaire (par exemple Cloudflare Pages Functions ou un service de formulaire gratuit) avant d'accepter des demandes.

## Source

Données ouvertes du SEAO, Données Québec : https://donneesquebec.ca/recherche/dataset/systeme-electronique-dappel-doffres-seao — attribution CC BY 4.0. Service indépendant.
