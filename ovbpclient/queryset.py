import collections

from .exceptions import RecordDoesNotExistError, MultipleRecordsReturnedError
from .models import BaseModel


class Queryset:
    def __init__(self, records):
        self.records_by_id = collections.OrderedDict((r.id, r) for r in records)

    def __len__(self):
        return len(self.records_by_id)

    def __iter__(self):
        return iter(self.records_by_id.values())

    def __getitem__(self, item):
        return list(self)[item]

    def select(self, filter_by=None):
        iterator = self.records_by_id.values() if filter_by is None else \
            filter(filter_by, self.records_by_id.values())
        return Queryset(iterator)

    def one(self, filter_by=None) -> BaseModel:
        if isinstance(filter_by, (str, int)):
            try:
                return self.records_by_id[filter_by]
            except KeyError:
                raise RecordDoesNotExistError(
                    f"Queryset contains no record whose id is '{filter_by}'"
                )

        # filter if needed
        qs = self if filter_by is None else self.select(filter_by=filter_by)

        # check one and only one
        if len(qs) == 0:
            raise RecordDoesNotExistError(
                f"Queryset of contains no value.")
        if len(qs) > 1:
            raise MultipleRecordsReturnedError(
                f"Queryset of table contains more than one value.")

        # return record
        return qs[0]
