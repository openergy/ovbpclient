"""
Only transverse exceptions must come here. Contextual exceptions must be written in concerned module/package.
"""


class OVBPClientError(Exception):
    pass


class HttpError(OVBPClientError):
    def __init__(self, message="Client error", code=None):
        self.message = message
        self.code = code

    def __str__(self):
        return "Error code: %s.\nContent:\n\n%s" % (self.code, self.message)


class RecordDoesNotExistError(OVBPClientError):
    pass


class MultipleRecordsReturnedError(OVBPClientError):
    pass
