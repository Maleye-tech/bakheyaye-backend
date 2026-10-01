# BakhYayeCouture – Backend (Django + DRF + PostgreSQL + Cloudinary)

## Installation
```bash
python -m venv venv && source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # puis remplir DATABASE_URL et CLOUDINARY_URL
python manage.py migrate
python manage.py createsuperuser                      # compte du tailleur (accès au back-office)
python manage.py runserver                            # http://localhost:8000
```
- `DATABASE_URL` : PostgreSQL (ex. `postgres://user:pass@localhost:5432/bakhyaye`). Si vide → SQLite (test rapide).
- `CLOUDINARY_URL` : variable « API Environment » de votre console Cloudinary. Si vide → images stockées en local (`media/`).
- Données de démonstration (sans images) : `python manage.py seed_demo`

## API
| Méthode | URL | Description |
|---|---|---|
| GET | `/api/tenues/` | Liste **paginée** (12/page), **plus récentes d'abord** |
| GET | `/api/tenues/?size=M` | Filtre par taille (aussi `category` (id), `status`, `favorite`, `min_price`, `max_price`, `search`, `page`, `page_size`) |
| GET | `/api/tenues/{id}/` | Détail |
| POST / PATCH / DELETE | `/api/tenues/` … | Création / modification / suppression (admin) |
| POST | `/api/tenues/{id}/toggle-favorite/` | Coup de cœur on/off (admin) |
| POST | `/api/tenues/{id}/set-status/` | `{"status": "available" ou "sold_out"}` (admin) |
| POST | `/api/tenues/{id}/images/` | Upload multipart, champ `images` (admin) |
| DELETE | `/api/tenues/{id}/images/{image_id}/` | Supprimer une image (admin) |
| GET / POST / PATCH / DELETE | `/api/categories/` | Catégories (types de tenues) — lecture publique, gestion par l'admin |
| GET | `/api/meta/` | Tailles et types existants (pour les filtres) |
| POST | `/api/auth/token/` | Connexion (JWT) |

Lecture publique ; écriture réservée aux comptes `is_staff`. L'interface Django `/admin/` est aussi disponible.

## Déploiement (Render / Railway)
- Build : `./build.sh` — Start : `gunicorn config.wsgi`
- Variables : `SECRET_KEY`, `DEBUG=0`, `ALLOWED_HOSTS`, `DATABASE_URL`, `CLOUDINARY_URL`,
  `CORS_ALLOWED_ORIGINS=https://votre-frontend.vercel.app`, `CSRF_TRUSTED_ORIGINS=https://votre-frontend.vercel.app`
