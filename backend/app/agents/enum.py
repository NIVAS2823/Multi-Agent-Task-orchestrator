from enum import Enum

class SupervisorState(str, Enum):
    START = "start"
    PLAN = "plan"
    EXECUTE = "execute"
    CRITIQUE = "critique"
    ADVANCE = "advance"
    COMPLETE = "complete"
    FAIL = "fail"
