from enum import Enum
from app.graphs.state import AgentState
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_RETRIES = 3


class SupervisorState(str, Enum):
    START = "start"
    PLAN = "plan"
    EXECUTE = "execute"
    CRITIQUE = "critique"
    ADVANCE = "advance"
    COMPLETE = "complete"
    FAIL = "fail"


def supervisor_node(state: AgentState) -> dict:
    # -------------------- STATE EXTRACTION --------------------
    events = state.get("events", [])
    plan = state.get("plan") or []
    step_index = state.get("current_step_index", 0)
    retry_count = state.get("retry_count", 0)
    fsm_state = state.get("fsm_state", SupervisorState.START)

    current_step = state.get("current_step")

    execution_result = state.get("execution_result")
    critique = state.get("critique")
    is_approved = state.get("is_approved")

    last_output = state.get("last_executor_output")

    # -------------------- LOGGING HELPER --------------------
    def log(action: str, detail: str | None = None):
        msg = f"[SUPERVISOR][{fsm_state}] {action}"
        if detail:
            msg += f" - {detail}"
        logger.info(msg)

        events.append(
            {
                "agent": "supervisor",
                "action": action,
                "detail": detail,
                "step_index": step_index,
            }
        )

    # -------------------- TERMINAL RETRY GUARD --------------------
    if retry_count >= MAX_RETRIES:
        log("retry_limit_reached", "Forcing graceful completion")

        return {
            "events": events,
            "fsm_state": SupervisorState.COMPLETE,
            "next_agent": "end",
            "final_output": (
                last_output
                or execution_result
                or "Task stopped after repeated failures. Partial output returned."
            ),
        }

    # -------------------- FSM CORRECTION GUARD --------------------
    # Safety net: if plan exists but FSM somehow stayed in START
    if fsm_state == SupervisorState.START and plan:
        logger.warning(
            "FSM stuck in START with existing plan — correcting to EXECUTE"
        )
        fsm_state = SupervisorState.EXECUTE

    # ======================== FSM ========================

    # -------- START → PLAN --------
    if fsm_state == SupervisorState.START:
        log("start")
        return {
            "events": events,
            "fsm_state": SupervisorState.PLAN,
            "next_agent": "planner",
        }

    # -------- PLAN → EXECUTE --------
    if fsm_state == SupervisorState.PLAN:
        log("plan_ready")
        return {
            "events": events,
            "fsm_state": SupervisorState.EXECUTE,
            "current_step": plan[step_index],
            "next_agent": "executor",
        }

    # -------- EXECUTE → CRITIQUE --------
    if fsm_state == SupervisorState.EXECUTE:
        log("executing", current_step)
        return {
            "events": events,
            "fsm_state": SupervisorState.CRITIQUE,
            "next_agent": "critic",
        }

    # -------- CRITIQUE → ADVANCE / RETRY --------
    if fsm_state == SupervisorState.CRITIQUE:

        if is_approved is True:
            log("approved")
            return {
                "events": events,
                "fsm_state": SupervisorState.ADVANCE,
            }

        log("rejected", critique)
        return {
            "events": events,
            "fsm_state": SupervisorState.EXECUTE,
            "retry_count": retry_count + 1,
            "execution_result": None,
            "critique": None,
            "is_approved": None,
            "next_agent": "executor",
        }

    # -------- ADVANCE → NEXT STEP / COMPLETE --------
    if fsm_state == SupervisorState.ADVANCE:
        next_index = step_index + 1

        if next_index >= len(plan):
            log("complete_all_steps")
            return {
                "events": events,
                "fsm_state": SupervisorState.COMPLETE,
                "next_agent": "end",
                "final_output": last_output or execution_result,
            }

        log("advance_step", f"{next_index + 1}/{len(plan)}")
        return {
            "events": events,
            "fsm_state": SupervisorState.EXECUTE,
            "current_step_index": next_index,
            "current_step": plan[next_index],
            "retry_count": 0,
            "execution_result": None,
            "critique": None,
            "is_approved": None,
            "next_agent": "executor",
        }

    # -------------------- FALLBACK --------------------
    log("unexpected_state", str(fsm_state))
    return {
        "events": events,
        "fsm_state": SupervisorState.FAIL,
        "next_agent": "end",
        "final_output": last_output or "Unexpected termination. Partial output returned.",
    }
