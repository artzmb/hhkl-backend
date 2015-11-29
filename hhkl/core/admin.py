from django.contrib import admin

from core.models import Season, League, Player, Day, Match, Period


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    pass


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    pass


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    pass
