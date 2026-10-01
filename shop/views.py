from django.db.models import Count, Max
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .filters import TenueFilter
from .models import Category, Tenue, TenueImage
from .serializers import (
    SIZE_ORDER,
    CategorySerializer,
    ImageUploadSerializer,
    TenueImageSerializer,
    TenueSerializer,
)


class TenueViewSet(ModelViewSet):
    """
    GET    /api/tenues/                 liste paginée (plus récentes d'abord)
           ?size=M &category=Boubou &status=available &favorite=true &search=... &page=2
    GET    /api/tenues/{id}/            détail
    POST   /api/tenues/                 création (admin)
    PATCH  /api/tenues/{id}/            modification (admin)
    DELETE /api/tenues/{id}/            suppression (admin)
    POST   /api/tenues/{id}/toggle-favorite/   coup de cœur on/off (admin)
    POST   /api/tenues/{id}/set-status/        {"status": "available" | "sold_out"} (admin)
    POST   /api/tenues/{id}/images/            upload multipart, champ "images" (admin)
    DELETE /api/tenues/{id}/images/{image_id}/ suppression d'une image (admin)
    """

    serializer_class = TenueSerializer
    filterset_class = TenueFilter
    search_fields = ["name", "description", "fabric", "category__name"]
    ordering_fields = ["created_at", "price", "name"]
    ordering = ["-created_at", "-id"]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        return Tenue.objects.select_related("category").prefetch_related("images").order_by("-created_at", "-id")

    @action(detail=True, methods=["post"], url_path="toggle-favorite")
    def toggle_favorite(self, request, pk=None):
        tenue = self.get_object()
        tenue.is_favorite = not tenue.is_favorite
        tenue.save(update_fields=["is_favorite", "updated_at"])
        return Response(self.get_serializer(tenue).data)

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        tenue = self.get_object()
        new_status = request.data.get("status")
        if new_status not in Tenue.Status.values:
            return Response(
                {"status": ["Valeur invalide (available ou sold_out)."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tenue.status = new_status
        tenue.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(tenue).data)

    @action(detail=True, methods=["post"], url_path="images", parser_classes=[MultiPartParser, FormParser])
    def add_images(self, request, pk=None):
        tenue = self.get_object()
        files = request.FILES.getlist("images")
        ser = ImageUploadSerializer(data={"images": files})
        ser.is_valid(raise_exception=True)
        last = tenue.images.aggregate(m=Max("position"))["m"]
        pos = 0 if last is None else last + 1
        for f in ser.validated_data["images"]:
            TenueImage.objects.create(tenue=tenue, image=f, position=pos)
            pos += 1
        tenue = self.get_queryset().get(pk=tenue.pk)
        return Response(self.get_serializer(tenue).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path=r"images/(?P<image_id>\d+)")
    def delete_image(self, request, pk=None, image_id=None):
        tenue = self.get_object()
        image = tenue.images.filter(pk=image_id).first()
        if not image:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.image.delete(save=False)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(ModelViewSet):
    """Catégories (types de tenues) : lecture publique, gestion par l'admin. Non paginé."""

    serializer_class = CategorySerializer
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        return Category.objects.annotate(tenues_count=Count("tenues")).order_by("-created_at", "-id")


class MetaView(APIView):
    """Valeurs utiles pour alimenter les filtres du site."""

    permission_classes = []

    def get(self, request):
        categories = list(
            Category.objects.annotate(n=Count("tenues"))
            .filter(n__gt=0)
            .order_by("position", "name")
            .values("id", "name")
        )
        used = set()
        for sizes in Tenue.objects.values_list("sizes", flat=True):
            used.update(sizes or [])
        sizes = sorted(used, key=lambda s: (SIZE_ORDER.index(s) if s in SIZE_ORDER else 99, s))
        return Response({"categories": categories, "sizes": sizes})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "username": u.username, "is_staff": u.is_staff})
