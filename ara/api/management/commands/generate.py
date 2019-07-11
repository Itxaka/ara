from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from ara.api.models import Play, Playbook, File, FileContent
from ara.api.models import Host, Result, Task, Label, Record
from ara.api.serializers import DetailedFileSerializer, TaskSerializer, PlaybookSerializer, PlaySerializer
import os


class Command(BaseCommand):
    help = "Generates a static tree of the web application"

    @staticmethod
    def create_dirs(path):
        # create main output dir
        if not os.path.exists(path):
            os.mkdir(path)

        # create subdirs
        dirs = ["play"]
        for dir in dirs:
            if not os.path.exists(os.path.join(path, dir)):
                os.mkdir(os.path.join(path, dir))

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path where the static files will be built in", type=str)

    def handle(self, *args, **options):
        path = options.get("path")
        self.create_dirs(path)

        print("Generating static files at {}...".format(path))

        rendered = render_to_string(
            "index.html", {
                "plays": [PlaySerializer(p).data for p in Play.objects.all()],
                "page": "index"  # this is so I can hide the back button in the index
            }
        )
        with open(os.path.join(path, "index.html"), "w") as index:
            index.write(rendered)

        for play in Play.objects.all():

            playbooks = [
                PlaybookSerializer(p).data for p in Playbook.objects.filter(pk=play.playbook_id)
            ]
            tasks = [
                TaskSerializer(t).data for t in Task.objects.filter(play__id=play.pk).select_related()
            ]
            files = [
                DetailedFileSerializer(p).data for p in File.objects.filter(
                    playbook__id__in=[p['id'] for p in playbooks]
                )
            ]
            rendered = render_to_string("play.html", {
                "play": play,
                "playbooks": playbooks,
                "tasks": tasks,
                "files": files
            })

            with open(os.path.join(path, "play/", "{}.html".format(play.id)), "w") as p:
                p.write(rendered)
