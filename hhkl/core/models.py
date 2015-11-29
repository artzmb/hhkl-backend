from django.db import models


class Season(models.Model):
    def __unicode__(self):
        return "Season #%d" % (self.id,)


class League(models.Model):
    season = models.ForeignKey(Season)
    level = models.CharField(max_length=50)

    def __unicode__(self):
        return "S%d League #%s" % (self.season_id, self.level,)


class Player(models.Model):
    name = models.CharField(max_length=200)
    alias = models.CharField(max_length=3)
    league = models.ForeignKey(League)

    def __unicode__(self):
        return "%s (league #%s)" % (self.name, self.league_id,)


class Day(models.Model):
    league = models.ForeignKey(League)
    number = models.IntegerField(primary_key=True, unique=True)

    def __unicode__(self):
        return "S%dL%s Day #%d" % (self.league.season_id, self.league_id, self.number,)


class Match(models.Model):
    STATUSES = (
        (0, 'Idle'),
        (1, 'Running'),
        (2, 'Completed'),
        (3, 'Approved'),
        (4, 'Postponed')
    )
    day = models.ForeignKey(Day)
    yellow = models.ForeignKey(Player, related_name='yellow')
    red = models.ForeignKey(Player, related_name='red')
    status = models.IntegerField(choices=STATUSES)

    def __unicode__(self):
        return "%s - %s" % (self.yellow.name, self.red.name, )


class Period(models.Model):
    match = models.ForeignKey(Match)
    yellow = models.IntegerField()
    red = models.IntegerField()


class Table(models.Model):
    TYPES = (
        (0, 'Brief'),
        (1, 'Yellow'),
        (2, 'Red')
    )
    league = models.OneToOneField(League)
    type = models.IntegerField(choices=TYPES)


class TableRow(models.Model):
    table = models.ForeignKey(Table)
    position = models.IntegerField()
    player = models.ForeignKey(Player)
    played = models.IntegerField()
    wins = models.IntegerField()
    overtimeWins = models.IntegerField()
    overtimeLosses = models.IntegerField()
    losses = models.IntegerField()
    goalsFor = models.IntegerField()
    goalsAgainst = models.IntegerField()
    points = models.IntegerField()
