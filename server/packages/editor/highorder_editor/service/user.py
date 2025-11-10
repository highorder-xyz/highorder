
from highorder_editor.model import UserModel, ApplicationModel
from highorder_editor.service.application import Application


class User:

    @classmethod
    def load(cls, user_id):
        try:
            user = UserModel.get(UserModel.user_id == user_id)
            return cls(user)
        except UserModel.DoesNotExist:
            raise Exception('User not exists')


    def __init__(self, model):
        self._model = model

    @property
    def user_id(self):
        return self._model.user_id

    @property
    def email(self):
        return self._model.email


    @property
    def nickname(self):
        return self._model.nickname

    @nickname.setter
    def nickname(self, nickname):
        self._model.nickname = nickname

    def save(self):
        self._model.save()

    def list_applications(self):
        """List all applications - all users can access all apps"""
        applications = []
        applist = ApplicationModel.select()
        for app in applist:
            applications.append(Application(app))
        return applications
