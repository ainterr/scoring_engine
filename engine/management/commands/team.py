from django.core.management.base import BaseCommand, CommandError
from engine import models

class Command(BaseCommand):
    help = 'An endpoint for managing Scoring Engine teams'
    
    def add_arguments(self, parser):
        parser.add_argument('command', help='list, add, delete')
        parser.add_argument('team', nargs='?', help='A uniquely identifiable team name')

    def add_team(self, team_name):
        teams = models.Team.objects.filter(name=team_name)

        if teams:
            print('Error: Team name "{}" is already in use'.format(team_name))
        else:
            team = models.Team(name=team_name)
            team.save()
            print('Team "{}" created - id={}'.format(team_name, team.id))
        
    def remove_team(self, team_name):
        try:
            team = models.Team.objects.get(name=team_name)
        except models.Team.ObjectDoesNotExist:
            print('Error: Team name "{}" does not exist'.format(team_name))

        team.delete()
        print('Team "{}" deleted'.format(team_name))

    def list_teams(self):
        teams = models.Team.objects.all()

        for team in teams:
            print(team)

    def handle(self, *args, **options):
        command = options['command']

        if command == 'add':
            if options['team']: self.add_team(options['team'])
            else: print('Error: No team name specified')
        elif command == 'delete':
            if options['team']: self.remove_team(options['team'])
            else: print('Error: No team name specified')
        elif command == 'list':
            self.list_teams()
        else:
            print('Error: Invalid command "{}"'.format(command))
