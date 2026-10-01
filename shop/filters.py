import django_filters
from django.db.models import TextField
from django.db.models.functions import Cast

from .models import Tenue


class TenueFilter(django_filters.FilterSet):
    # ?size=M  -> tenues disponibles dans la taille M (filtrage côté serveur)
    size = django_filters.CharFilter(method="filter_size")
    category = django_filters.NumberFilter(field_name="category_id")
    status = django_filters.ChoiceFilter(choices=Tenue.Status.choices)
    favorite = django_filters.BooleanFilter(field_name="is_favorite")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Tenue
        fields = ["size", "category", "status", "favorite", "min_price", "max_price"]

    def filter_size(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset
        # Fonctionne sur PostgreSQL (jsonb) comme sur SQLite : on cherche "M" dans la liste JSON.
        return queryset.annotate(_sizes_txt=Cast("sizes", TextField())).filter(
            _sizes_txt__contains=f'"{value}"'
        )
