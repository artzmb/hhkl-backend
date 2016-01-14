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
    number = models.IntegerField()
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return "S%dL%s Day #%d" % (self.league.season_id, self.league_id, self.number,)


IDLE = 0
RUNNING = 1
COMPLETED = 2
APPROVED = 3
POSTPONED = 4


class Match(models.Model):
    STATUSES = (
        (IDLE, 'Idle'),
        (RUNNING, 'Running'),
        (COMPLETED, 'Completed'),
        (APPROVED, 'Approved'),
        (POSTPONED, 'Postponed')
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


BRIEF = 'brief'
YELLOW = 'yellow'
RED = 'red'


class Table(models.Model):
    TYPES = (
        (BRIEF, 'Brief'),
        (YELLOW, 'Yellow'),
        (RED, 'Red')
    )
    league = models.OneToOneField(League)
    type = models.CharField(choices=TYPES, max_length=50)


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
