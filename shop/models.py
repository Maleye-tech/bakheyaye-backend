from django.db import models


class Category(models.Model):
    name = models.CharField("nom", max_length=80, unique=True)
    position = models.PositiveSmallIntegerField("ordre d'affichage", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "name"]
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self):
        return self.name


class Tenue(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponible"
        SOLD_OUT = "sold_out", "Épuisé"

    name = models.CharField("nom", max_length=150)
    description = models.TextField("description", blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name="catégorie",
        related_name="tenues",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    fabric = models.CharField("type de tissu", max_length=120, blank=True)
    price = models.PositiveIntegerField("prix (FCFA)")
    sizes = models.JSONField("tailles", default=list, blank=True, help_text='Ex : ["S", "M", "L"]')
    colors = models.JSONField(
        "couleurs disponibles",
        default=list,
        blank=True,
        help_text='Ex : [{"name": "Bleu nuit", "hex": "#1b2a49"}]',
    )
    status = models.CharField(
        "statut", max_length=12, choices=Status.choices, default=Status.AVAILABLE, db_index=True
    )
    is_favorite = models.BooleanField("coup de cœur", default=False, db_index=True)
    created_at = models.DateTimeField("créée le", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("modifiée le", auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "tenue"
        verbose_name_plural = "tenues"

    def __str__(self):
        return self.name


class TenueImage(models.Model):
    tenue = models.ForeignKey(Tenue, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField("image", upload_to="bakhyaye/tenues")
    position = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "image"
        verbose_name_plural = "images"

    def __str__(self):
        return f"Image {self.pk} – {self.tenue_id}"
