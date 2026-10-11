import re

# Names from the game's tables (wago, simulator) include internal dev creatures: tagged ones like "[DNT] FX Bunny",
# "Gronn (Black)", "<DNT> Smoke Plume", and helpers like "Spell Bunny" or "Kill Credit". Names seen in game
# (id collector) don't need this, they are real by definition.
# The addon looks npc ids up by the name shown in game, so these names would only add dead entries.
BANNED_NAME_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [
    r"[\[\]<>()]",                                        # any tag: [DNT] [UNUSED] [PH] <DNT> (IGC) (Red) ...
    r"\bUNUSED\b",
    r"\bDNT\b",
    r"\bDND\b",
    r"\bdo not (use|translate)\b",
    r"\bdelete me\b",
    r"\bplaceholder\b",
    r"\btest (npc|creature|battlepet)\b",
    r"\bkill credit\b",
    r"\bbunny\b",
    r"\b(invisible|sound|spell|fx|general purpose) stalker\b",
]]


def is_banned_name(name):
    return any(pattern.search(name) for pattern in BANNED_NAME_PATTERNS)
