import django.db.models.deletion
from django.db import migrations, models


def strings_to_categories(apps, schema_editor):
    Category = apps.get_model("shop", "Category")
    Tenue = apps.get_model("shop", "Tenue")
    cache = {}
    for t in Tenue.objects.exclude(category=""):
        name = t.category.strip()
        if not name:
            continue
        key = name.lower()
        if key not in cache:
            cache[key] = Category.objects.get_or_create(name=name)[0]
        t.category_fk = cache[key]
        t.save(update_fields=["category_fk"])


class Migration(migrations.Migration):
    dependencies = [("shop", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True, verbose_name="nom")),
                ("position", models.PositiveSmallIntegerField(default=0, verbose_name="ordre d'affichage")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name": "catégorie", "verbose_name_plural": "catégories", "ordering": ["position", "name"]},
        ),
        migrations.AddField(
            model_name="tenue",
            name="category_fk",
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tenues", to="shop.category"),
        ),
        migrations.RunPython(strings_to_categories, migrations.RunPython.noop),
        migrations.RemoveField(model_name="tenue", name="category"),
        migrations.RenameField(model_name="tenue", old_name="category_fk", new_name="category"),
        migrations.AlterField(
            model_name="tenue",
            name="category",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tenues", to="shop.category", verbose_name="catégorie"),
        ),
    ]
