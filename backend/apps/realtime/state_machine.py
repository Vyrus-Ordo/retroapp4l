from enum import Enum


class Phase(str, Enum):
    SETUP = "setup"
    LOBBY = "lobby"
    PRESENTATION = "presentation"
    CHECK = "check"
    BOARD = "board"
    GROUPING = "grouping"
    VOTING = "voting"
    DISCUSSION = "discussion"
    ACTIONS = "actions"
    CLOSED = "closed"


PHASE_TRANSITIONS = {
    Phase.SETUP: [Phase.LOBBY],
    Phase.LOBBY: [Phase.PRESENTATION],
    Phase.PRESENTATION: [Phase.CHECK],
    Phase.CHECK: [Phase.BOARD],
    Phase.BOARD: [Phase.GROUPING],
    Phase.GROUPING: [Phase.VOTING],
    Phase.VOTING: [Phase.DISCUSSION],
    Phase.DISCUSSION: [Phase.ACTIONS],
    Phase.ACTIONS: [Phase.CLOSED],
    Phase.CLOSED: [],
}

def is_valid_transition(current, target):
    return target in PHASE_TRANSITIONS.get(current, [])
