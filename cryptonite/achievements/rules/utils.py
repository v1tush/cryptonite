import importlib
import pkgutil

from achievements.rules import __path__
from achievements.rules.base import AchievementAbstract


def load_rules():
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f'achievements.rules.{module_name}')


def get_rules():
    load_rules()
    return [cls() for cls in AchievementAbstract.__subclasses__()]
