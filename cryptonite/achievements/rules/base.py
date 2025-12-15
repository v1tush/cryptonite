import abc


class AchievementAbstract(abc.ABC):
    achievement_code: str

    @abc.abstractmethod
    def is_achieved(self, user) -> bool:
        ...
