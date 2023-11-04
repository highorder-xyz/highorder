from postmodel import models
import copy

DB_NAME = 'highorder'

class MetaverModel(models.Model):
    created = models.DatetimeField(auto_now_add=True)
    updated = models.DatetimeField(auto_now=True)
    data_ver = models.DataVersionField()

    class Meta:
        abstract = True

    @classmethod
    def load_from(cls, data):
        kwargs = copy.copy(data)
        if 'created' in kwargs and kwargs['created'] == None:
            del kwargs['created']
        if 'updated' in kwargs and kwargs['updated'] == None:
            del kwargs['updated']
        return cls(**kwargs)


    def render_to(self):
        data = self.to_jsondict()
        if data['created'] == None:
            del data['created']
        if data['updated'] == None:
            del data['updated']
        return data
