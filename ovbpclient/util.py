from .exceptions import RecordDoesNotExistError, MultipleRecordsReturnedError


def get_one_and_only_one(records_list, condition=None):
    """
    Parameters
    ----------
    records_list: records list
    condition:
        if None, whole list will be used
        if str, condition on id
        if callable, condition will be applied

    Returns
    -------
    record
    """
    if isinstance(condition, (str, int)):
        def condition(x):
            return x.id == condition

    # filter if needed
    unique_record = records_list if condition is None else list(filter(condition, records_list))

    # check one and only one
    if len(unique_record) == 0:
        raise RecordDoesNotExistError(f"No record verifying condition was found.")
    if len(unique_record) > 1:
        raise MultipleRecordsReturnedError(f"More than one record verifying condition was found.")

    # return record
    return unique_record[0]
