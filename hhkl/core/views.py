import json
from collections import namedtuple

from django.db import connection
from django.http import HttpResponse
from django.views.generic import TemplateView, View

from core.models import Day, Season, Match, Period


def named_tuple_fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


class IndexView(TemplateView):
    template_name = "core/index.html"


class MatchesView(View):
    def get(self, request, *args, **kwargs):
        league_level = kwargs["league_level"]
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                core_match.id AS id,
                day.number AS day,
                yellow.id AS yellow_id,
                yellow.name AS yellow_name,
                yellow.alias AS yellow_alias,
                red.id AS red_id,
                red.name AS red_name,
                red.alias AS red_alias,
                core_match.status AS status
            FROM core_match
            JOIN core_player red ON core_match.red_id = red.id
            JOIN core_player yellow ON core_match.yellow_id = yellow.id
            JOIN core_day day ON core_match.day_id = day.number
            JOIN core_league ON day.league_id = core_league.id
            JOIN core_season ON core_league.season_id = core_season.id
            WHERE core_league.level = %s
                AND core_season.id = (SELECT core_season.id FROM core_season ORDER BY core_season.id DESC LIMIT 1)
        """, (league_level,))

        rows = named_tuple_fetchall(cursor)
        match_ids = []
        scores = {}
        for row in rows:
            match_ids.append(row.id)
            scores[row.id] = []

        periods = Period.objects.filter(match__id__in=match_ids).all()
        for period in periods:
            scores[period.match_id].append((period.yellow, period.red,))

        days = {}
        for row in rows:
            if not days.get(row.day):
                days[row.day] = []
            days[row.day].append({
                "id": row.id,
                "yellow": {
                    "id": row.yellow_id,
                    "name": row.yellow_name,
                    "alias": row.yellow_alias,
                },
                "red": {
                    "id": row.red_id,
                    "name": row.red_name,
                    "alias": row.red_alias,
                },
                "status": row.status,
                "score": scores.get(row.id)
            })

        return HttpResponse(json.dumps({"days": days}), content_type="application/json")


class PlayersView(View):
    def get(self, request, *args, **kwargs):
        league_level = kwargs["league_level"]
        cursor = connection.cursor()
        cursor.execute("""
            SELECT core_player.id AS id, core_player.name AS name, core_player.alias AS alias
            FROM core_player
            JOIN core_league ON core_player.league_id = core_league.id
            JOIN core_season ON core_league.season_id = core_season.id
            WHERE core_league.level = %s
              AND core_season.id = (SELECT core_season.id FROM core_season ORDER BY core_season.id DESC LIMIT 1)
        """, (league_level,))

        rows = named_tuple_fetchall(cursor)
        players = []
        for row in rows:
            players.append({
                "id": row.id,
                "name": row.name,
                "alias": row.alias,
            })

        return HttpResponse(json.dumps({"players": players}), content_type="application/json")

    