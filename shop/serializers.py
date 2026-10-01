import re

from rest_framework import serializers

from .models import Category, Tenue, TenueImage

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
SIZE_ORDER = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"]


def optimized(url, transformation):
    """Ajoute une transformation Cloudinary (format/qualité auto, redimensionnement)."""
    if url and "res.cloudinary.com" in url and "/upload/" in url:
        return url.replace("/upload/", f"/upload/{transformation}/", 1)
    return url


class TenueImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    thumb = serializers.SerializerMethodField()
    full = serializers.SerializerMethodField()

    class Meta:
        model = TenueImage
        fields = ["id", "url", "thumb", "full", "position"]

    def _abs(self, obj):
        url = obj.image.url
        request = self.context.get("request")
        if request and url.startswith("/"):
            return request.build_absolute_uri(url)
        return url

    def get_url(self, obj):
        return optimized(self._abs(obj), "f_auto,q_auto,w_900")

    def get_thumb(self, obj):
        return optimized(self._abs(obj), "f_auto,q_auto,w_500,c_fill,ar_4:5,g_auto")

    def get_full(self, obj):
        return optimized(self._abs(obj), "f_auto,q_auto,w_1600")


class CategorySerializer(serializers.ModelSerializer):
    tenues_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ["id", "name", "position", "tenues_count"]

    def validate_name(self, value):
        value = value.strip()
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Cette catégorie existe déjà.")
        return value


class TenueSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), allow_null=True, required=False
    )
    category_name = serializers.SerializerMethodField()
    images = TenueImageSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Tenue
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_name",
            "fabric",
            "price",
            "sizes",
            "colors",
            "status",
            "status_display",
            "is_favorite",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_category_name(self, obj):
        return obj.category.name if obj.category_id else ""

    def validate_sizes(self, value):
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise serializers.ValidationError("Liste de tailles invalide.")
        cleaned = []
        for v in value:
            v = v.strip().upper()
            if v and v not in cleaned:
                cleaned.append(v)
        cleaned.sort(key=lambda s: (SIZE_ORDER.index(s) if s in SIZE_ORDER else 99, s))
        return cleaned

    def validate_colors(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Liste de couleurs invalide.")
        cleaned = []
        for c in value:
            if not isinstance(c, dict) or not str(c.get("name", "")).strip():
                raise serializers.ValidationError("Chaque couleur doit avoir un nom.")
            hex_ = str(c.get("hex", "")).strip()
            if hex_ and not HEX_RE.match(hex_):
                raise serializers.ValidationError(f"Code couleur invalide : {hex_}")
            cleaned.append({"name": str(c["name"]).strip(), "hex": hex_ or "#999999"})
        return cleaned


class ImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(), allow_empty=False, max_length=10
    )
