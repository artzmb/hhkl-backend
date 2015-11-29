from tastypie.resources import ModelResource

from core.models import Match


class MatchResource(ModelResource):
    class Meta:
        queryset = Match.objects.all()
        resource_name = 'matches'