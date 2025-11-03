import sys
import time
import statistics
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, List

# Color class for console output
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

def supports_color() -> bool:
    return sys.stdout.isatty()

USE_COLOR = supports_color()

def col(text: str, code: str) -> str:
    return f"{code}{text}{C.RESET}" if USE_COLOR else text

def header(text: str):
    print(col("\n" + text.center(78) + "\n", C.MAGENTA + C.BOLD))

# Thresholds
ON_THRESHOLD = 150
VERY_BRIGHT = 1000
NIGHT_START = 20
NIGHT_END = 6
AVG_WINDOW = 3

# Emojis for actions
EMOJI = {
    'on': '💡',
    'off': '🔌',
    'dim': '🌙',
    'bright': '☀️'
}

@dataclass
class Percept:
    time_hour: int
    occupied: bool
    lux: float
    manual_override: Optional[str] = None
    user_pref: Optional[Dict] = None
    blinds_closed: bool = False

def night_hours(h: int) -> bool:
    return (h >= NIGHT_START) or (h < NIGHT_END)

def smart_light_decide(percept: Percept, recent_lux: List[float]) -> Tuple[str, str, str]:
    avg_lux = statistics.mean(recent_lux[-AVG_WINDOW:]) if recent_lux else percept.lux

    if percept.manual_override == 'ON':
        return "TurnOn_Full", "ManualOverride", "User requested ON"
    if percept.manual_override == 'OFF':
        return "TurnOff", "ManualOverride", "User requested OFF"
    if not percept.occupied:
        return "TurnOff", "Unoccupied", "No occupant detected"
    if avg_lux >= VERY_BRIGHT and not percept.blinds_closed:
        return "TurnOff", "VeryBrightAmbient", f"AvgLux={avg_lux:.0f} >= {VERY_BRIGHT}"
    if avg_lux < ON_THRESHOLD:
        if night_hours(percept.time_hour):
            return "TurnOn_Dim", "DarkAtNight", f"AvgLux={avg_lux:.0f} < {ON_THRESHOLD} and night"
        else:
            return "TurnOn_Full", "DarkDaytime", f"AvgLux={avg_lux:.0f} < {ON_THRESHOLD}"

    # Handle user preferences
    pref = percept.user_pref or {}
    prefer_energy = pref.get('prefer_energy', True)
    preferred_lux = pref.get('preferred_lux', None)
    if prefer_energy:
        return "TurnOff", "AmbientSufficient_EnergyPref", f"AvgLux={avg_lux:.0f} (user prefers energy)"
    if preferred_lux and preferred_lux > avg_lux + 20:
        gap = preferred_lux - avg_lux
        if gap > 150:
            return "TurnOn_Full", "UserPrefBoost_Full", f"Increase to {preferred_lux} lux"
        else:
            return "TurnOn_Dim", "UserPrefBoost_Dim", f"Increase to {preferred_lux} lux"
    return "NoOp", "AmbientOK", f"AvgLux={avg_lux:.0f} OK"

def print_example_table(rows: List[Tuple[Percept, str, str, str]]):
    print(col("\nExamples: Smart Light Decisions\n", C.BLUE + C.BOLD))
    print(col(f"{'Time':^6}|{'Occu':^6}|{'Lux':^6}|{'Manual':^8}|{'Action':^18}|{'Rule':^20}|{'Explain':^25}", C.BOLD))
    print("-" * 100)
    for p, action, rule, expl in rows:
        occ = "Yes" if p.occupied else "No"
        man = p.manual_override or "-"
        action_label = (EMOJI['on'] if "On" in action else EMOJI['dim'] if "Dim" in action else EMOJI['off']) + " " + action
        print(f"{p.time_hour:02d}:00 | {occ:^6}| {int(p.lux):^6} | {man:^8} | {action_label:^18} | {rule:^20} | {expl[:24]:24}")

def timeline_simulation(percepts: List[Percept], delay: float = 0.7):
    recent = []
    print(col("\nTimeline simulation (press Ctrl+C to stop):\n", C.MAGENTA + C.BOLD))
    for t, p in enumerate(percepts, start=1):
        recent.append(p.lux)
        action, rule, expl = smart_light_decide(p, recent)

        # Fixed: define action_icon before using
        action_icon = EMOJI['on'] if "TurnOn" in action else EMOJI['dim'] if "Dim" in action else EMOJI['off']
        avg_lux = statistics.mean(recent[-AVG_WINDOW:])
        status = f"Step {t:02d} | {p.time_hour:02d}:00 | Occ: {'Y' if p.occupied else 'N'} | Lux(avg):{avg_lux:5.0f}"
        print(col(status, C.CYAN))
        print(f" → Action: {col(action_icon + ' ' + action, C.GREEN if 'TurnOn' in action else C.YELLOW if 'Dim' in action else C.RED)}")
        print(f" → Rule: {col(rule, C.BLUE)} | Note: {expl}")
        print("-" * 70)
        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user.")
            break

def example_run():
    header("Smart Light — Beautiful Output")
    examples = [
        Percept(16, True, 50),
        Percept(14, True, 80),
        Percept(10, False, 70),
        Percept(9, True, 1500),
        Percept(5, True, 200),
        Percept(15, True, 180, user_pref={'prefer_energy': False, 'preferred_lux': 400}),
        Percept(21, True, 450, blinds_closed=True),
        Percept(14, True, 380, manual_override='ON'),
        Percept(18, True, 350, manual_override='OFF'),
    ]
    rows = []
    recent_l = []
    for p in examples:
        recent_l.append(p.lux)
        action, rule, expl = smart_light_decide(p, recent_l)
        rows.append((p, action, rule, expl))
    print_example_table(rows)

    timeline = [
        Percept(18, True, 400),
        Percept(19, True, 360),
        Percept(20, True, 220),
        Percept(21, True, 190),
        Percept(22, True, 160),
        Percept(23, True, 140),
        Percept(0, True, 120),
        Percept(1, True, 110),
        Percept(2, True, 105),
        Percept(3, True, 100),
        Percept(4, True, 95),
        Percept(5, True, 90),
    ]
    timeline_simulation(timeline, delay=0.25)

if __name__ == "__main__":
    example_run()
