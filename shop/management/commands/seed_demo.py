import random

from django.core.management.base import BaseCommand

from shop.models import Category, Tenue

CATALOGUE = [
    ("Grand Boubou Brodé Royal", "Boubou", "Bazin riche", 85000),
    ("Ensemble Complet Prestige", "Ensemble", "Getzner", 65000),
    ("Caftan Élégance Dakar", "Caftan", "Soie", 72000),
    ("Costume Africain Signature", "Costume", "Wax premium", 58000),
    ("Robe Sirène Teranga", "Robe", "Dentelle", 45000),
    ("Kaftan Homme Classique", "Caftan", "Coton", 38000),
    ("Tunique Brodée Or", "Tunique", "Bazin", 42000),
    ("Ensemble Pagne Tissé", "Ensemble", "Pagne tissé", 55000),
    ("Boubou Femme Lumière", "Boubou", "Voile", 48000),
    ("Costume Trois Pièces", "Costume", "Lin", 95000),
    ("Robe de Soirée Ndiaye", "Robe", "Satin", 60000),
    ("Grand Boubou Cérémonie", "Boubou", "Bazin riche", 110000),
    ("Ensemble Enfant Tabaski", "Ensemble", "Wax", 25000),
    ("Jupe & Top Assortis", "Ensemble", "Wax", 32000),
]
PALETTE = [
    ("Bleu nuit", "#1b2a49"),
    ("Blanc ivoire", "#f5efe0"),
    ("Bordeaux", "#6d1a2b"),
    ("Vert émeraude", "#0f5b46"),
    ("Or", "#c9a24b"),
    ("Noir", "#141414"),
    ("Terracotta", "#b5563a"),
]
SIZES = ["S", "M", "L", "XL", "XXL"]


class Command(BaseCommand):
    help = "Crée quelques tenues de démonstration (sans images)."

    def handle(self, *args, **options):
        rnd = random.Random(7)
        for name, cat, fabric, price in CATALOGUE:
            cat, _ = Category.objects.get_or_create(name=cat)
            Tenue.objects.get_or_create(
                name=name,
                defaults=dict(
                    category=cat,
                    fabric=fabric,
                    price=price,
                    description=f"{name} — confectionné sur mesure dans notre atelier avec un tissu {fabric.lower()} de qualité.",
                    sizes=sorted(rnd.sample(SIZES, rnd.randint(2, 5)), key=SIZES.index),
                    colors=[{"name": n, "hex": h} for n, h in rnd.sample(PALETTE, rnd.randint(1, 4))],
                    is_favorite=rnd.random() < 0.3,
                    status=Tenue.Status.SOLD_OUT if rnd.random() < 0.15 else Tenue.Status.AVAILABLE,
                ),
            )
        self.stdout.write(self.style.SUCCESS(f"{Tenue.objects.count()} tenues en base."))
