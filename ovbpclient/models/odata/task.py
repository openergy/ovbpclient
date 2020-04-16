import time
from ..base import BaseModel
from ...exceptions import TaskDidNotFinishSuccessfully

PENDING = "pending"
REFUSED = "refused"
CANCELLED = "cancelled"
FINISHED = "finished"
FAILED = "failed"
SERVER_ERROR = "server_error"
RUNNING = "running"
NOT_FOUND = "not_found"


class Task(BaseModel):
    def wait_for_completion(self, period=3000, raise_if_problem=True):
        """
        Parameters
        ----------
        period: number of milliseconds between successive data reloads
        raise_if_problem: bool

        Returns
        -------
        status
        """
        ms = 1e-3 * period
        while self.base["status"] in (PENDING, RUNNING):
            self.reload()
            time.sleep(ms)
        if raise_if_problem and self.base["status"] not in (FINISHED, REFUSED):
            raise TaskDidNotFinishSuccessfully(self.id, self.base["status"])

        return self.base["status"]
