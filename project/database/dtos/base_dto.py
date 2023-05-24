import json
import datetime

from project.common.decorators import lazy_property


class BaseDTO:
    def toJSON(self):
        return json.dumps(self, default=self.json_default, sort_keys=True, indent=4)

    @staticmethod
    def json_default(value):
        if isinstance(value, datetime.datetime):
            return dict(year=value.year, month=value.month, day=value.day, hour=value.hour, minute=value.minute, second=value.second)
        else:
            return value.__dict__

    @lazy_property
    def frontend_object(self):
        dict_params = self.__dict__
        return {key: value for key, value in dict_params.items() if not key.startswith('_')}
