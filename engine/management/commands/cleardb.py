from django.core.management.base import BaseCommand, CommandError
from engine import models
import sys

class Command(BaseCommand):
    help = 'This will blow away all data in the database. USE THIS WITH CAUTION'
    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
        prompt = " [y/N] "

        while True:
            sys.stdout.write("This will delete all data in the databse. Are you sure? [y/N] ")
            choice = raw_input().lower()

            if choice == '': return
            if choice in valid:
                if not valid[choice]: return
                else: break
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

        models.Team.objects.all().delete()
        models.Credential.objects.all().delete()
        models.UserProfile.objects.all().delete()
        models.Result.objects.all().delete()
        models.Service.objects.all().delete()
        models.Plugin.objects.all().delete()

        print("Database cleared")