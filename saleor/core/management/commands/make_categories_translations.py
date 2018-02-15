import logging
import os.path
import saleor

from pathlib import Path
from django.core.management import BaseCommand
from saleor.product.models import Category


MSG_ID = 'msgid '
HERE = os.path.dirname(saleor.__file__)
LOCALE_PATH = os.path.join(HERE, '..', 'locale')


def get_categories():
    for cat in Category.objects.all():
        yield cat


def read_po_file(fp):
    entries = set()

    line = fp.readline()

    while line:
        if line.startswith(MSG_ID):
            x = line.split(MSG_ID, 1)
            if len(x) > 1:
                msg_id = x[1].strip()
                entries.add(msg_id[1:-1])  # get and remove the quotes

        line = fp.readline()

    return entries


def _message_to_pot(message):
    message = message.replace('"', '\\"')

    return 'msgid "{}"\n' \
           'msgstr ""\n\n'.format(message)


def messages_to_pot(base_messages, new_messages):
    for msg_id in new_messages:
        if msg_id in base_messages:
            continue
        yield _message_to_pot(msg_id)


def get_locales_from_dir(base_path: Path, locale_name: str):
    for file in Path(base_path).iterdir():  # type: Path
        if not file.is_dir():
            continue

        locale_path = file / 'LC_MESSAGES' / locale_name
        if not locale_path.exists():
            if not locale_path.parent.exists():
                locale_path.parent.mkdir()
            locale_path.touch()
            logging.info('created: %s', locale_path)
        else:
            logging.info('Found: %s', locale_path)

        yield locale_path


class Command(BaseCommand):
    help = 'Populate database with test objects'
    placeholders_dir = r'saleor/static/placeholders/'

    def handle(self, *args, **options):
        msg_id_to_add = set()

        for cat in get_categories():
            msg_id_to_add.add(cat.name)

        for locale in get_locales_from_dir(Path(LOCALE_PATH), 'db_translations.po'):
            with locale.open(mode='r') as fp:
                pot_file = read_po_file(fp)
                pot_file = messages_to_pot(pot_file, msg_id_to_add)

            with locale.open(mode='a') as fp:
                fp.writelines(pot_file)
