from dal import autocomplete
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Manufacturer


class ManufacturerAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 100

    def get_queryset(self):
        qs = Manufacturer.objects.all()
        if self.q:
            qs = qs.filter(
                Q(mfr_name__icontains=self.q) | Q(mfr_full_id__icontains=self.q)
            )

        return qs


class ManufacturerUsernameAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = get_user_model().objects.all()
        if self.q:
            qs = qs.filter(Q(username__icontains=self.q) | Q(id__icontains=self.q))

        return qs


class ManufacturerCurrentUserAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        u = self.request.user
        qs = u.manufacturer_set.all()
        if self.q:
            qs = qs.filter(
                Q(mfr_name__icontains=self.q) | Q(mfr_full_id__icontains=self.q)
            )

        return qs
