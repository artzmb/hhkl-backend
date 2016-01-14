import json
from collections import namedtuple

from django.db import connection
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from core.models import Match, Period, Player, RED, COMPLETED, IDLE, YELLOW, APPROVED, BRIEF


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
                day.active AS active,
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
            JOIN core_day day ON core_match.day_id = day.id
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
                days[row.day] = {}
                days[row.day]["matches"] = []
                days[row.day]["name"] = row.day
                days[row.day]["active"] = row.active
            days[row.day]["matches"].append({
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

        return HttpResponse(json.dumps({"days": days.values()}), content_type="application/json")


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


class TableView(View):
    def get(self, request, *args, **kwargs):
        league_level = kwargs["league_level"]
        table_type = kwargs["table_type"]

        if table_type not in (BRIEF, YELLOW, RED,):
            return HttpResponse(json.dumps({"error" : "Only types brief, yellow and red allowed"}), status=400, content_type="application/json")

        standings = calculate_table(league_level, table_type)

        return HttpResponse(json.dumps({"standings": standings}), content_type="application/json")


class MatchView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(MatchView, self).dispatch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        match_id = kwargs["match_id"]

        try:
            body = json.loads(request.body)
        except ValueError:
            return HttpResponse(json.dumps({"error" : "Bad json"}), status=400, content_type="application/json")

        try:
            match = Match.objects.select_related().get(pk=match_id)
        except Match.DoesNotExist:
            return HttpResponse(json.dumps({"error" : "Match does not exist"}), status=404, content_type="application/json")

        if match.status == APPROVED:
            return HttpResponse(json.dumps({"error" : "Match already approved"}), status=403, content_type="application/json")

        for key in body.keys():
            if key != "status" and key != "score":
                return HttpResponse(json.dumps({"error" : "Only status and score field allowed"}), status=400, content_type="application/json")

        if "status" in body:
            status = body["status"]
            if status > COMPLETED or status < IDLE:
                return HttpResponse(json.dumps({"error" : "Only statuses 0, 1 and 2 allowed"}), status=400, content_type="application/json")
            match.status = body["status"]
            match.save()
        if "score" in body:
            Period.objects.filter(match_id=match).delete()
            for period in body["score"]:
                p = Period(match=match, yellow=period[0], red=period[1])
                p.save()

        response = {
            "id": match.id,
            "yellow": {
                "id": match.yellow.id,
                "name": match.yellow.name,
                "alias": match.yellow.alias,
            },
            "red": {
                "id": match.red.id,
                "name": match.red.name,
                "alias": match.red.alias,
            },
            "status": match.status,
            "score": []
        }

        periods = Period.objects.filter(match_id=match)
        for period in periods:
            response["score"].append((period.yellow, period.red,))

        return HttpResponse(json.dumps(response), content_type="application/json")


def calculate_table(league_level, table_type):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            core_match.id AS id,
            yellow.id AS yellow_id,
            red.id AS red_id,
            core_match.status AS status
        FROM core_match
        JOIN core_player red ON core_match.red_id = red.id
        JOIN core_player yellow ON core_match.yellow_id = yellow.id
        JOIN core_day day ON core_match.day_id = day.id
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

    table = {}
    players = Player.objects.filter(league__level=league_level)
    for player in players:
        table[player.id] = {
            "played": 0,
            "player": {
                "id": player.id,
                "name": player.name,
                "alias": player.alias
            },
            "wins": 0,
            "overtimeWins": 0,
            "overtimeLosses": 0,
            "losses": 0,
            "goalsFor": 0,
            "goalsAgainst": 0,
            "points": 0
        }

    for row in rows:
        periods = scores.get(row.id)
        yellow_score = 0
        red_score = 0
        yellow_goals = 0
        red_goals = 0
        if row.status == APPROVED:
            for period in periods:
                yellow_goals += period[0]
                red_goals += period[1]
                if period[0] > period[1]:
                    yellow_score += 1
                elif period[1] > period[0]:
                    red_score += 1

            if table_type != RED:
                table[row.yellow_id]["played"] += 1
                table[row.yellow_id]["goalsFor"] += yellow_goals
                table[row.yellow_id]["goalsAgainst"] += red_goals
            if table_type != YELLOW:
                table[row.red_id]["played"] += 1
                table[row.red_id]["goalsFor"] += red_goals
                table[row.red_id]["goalsAgainst"] += yellow_goals

            if yellow_score == 2 and red_score == 0 and table_type:
                if table_type != RED:
                    table[row.yellow_id]["wins"] += 1
                    table[row.yellow_id]["points"] += 3
                if table_type != YELLOW:
                    table[row.red_id]["losses"] += 1
            elif yellow_score == 2 and red_score == 1:
                if table_type != RED:
                    table[row.yellow_id]["overtimeWins"] += 1
                    table[row.yellow_id]["points"] += 2
                if table_type != YELLOW:
                    table[row.red_id]["overtimeLosses"] += 1
                    table[row.red_id]["points"] += 1
            elif yellow_score == 1 and red_score == 2:
                if table_type != RED:
                    table[row.yellow_id]["overtimeLosses"] += 1
                    table[row.yellow_id]["points"] += 1
                if table_type != YELLOW:
                    table[row.red_id]["overtimeWins"] += 1
                    table[row.red_id]["points"] += 2
            elif yellow_score == 0 and red_score == 2:
                if table_type != RED:
                    table[row.yellow_id]["losses"] += 1
                if table_type != YELLOW:
                    table[row.red_id]["wins"] += 1
                    table[row.red_id]["points"] += 3

    standings = table.values()

    standings.sort(key=lambda row: row["player"]["name"])
    standings.sort(key=lambda row: row["goalsFor"] - row["goalsAgainst"], reverse=True)
    standings.sort(key=lambda row: row["overtimeWins"], reverse=True)
    standings.sort(key=lambda row: row["wins"], reverse=True)
    standings.sort(key=lambda row: row["points"], reverse=True)

    i = 1
    for row in standings:
        row["position"] = i
        i += 1

    return standings

