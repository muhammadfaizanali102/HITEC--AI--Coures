import statistics
from collections import deque
TEMP_MIN = 20.0  
TEMP_MAX = 24.0  
TREND_THRESHOLD = 0.5  
MEMORY_SIZE = 5  

HEAT = "Heating ON 🔥"
COOL = "Cooling ON ❄️"
OFF = "System OFF ✅"

class ThermostatAgent:
    def __init__(self):
        self.past_temps = deque(maxlen=MEMORY_SIZE)
        self.last_action = OFF

    def sense(self, temp: float):
        """Sense the current temperature and store in memory."""
        self.past_temps.append(temp)
        print(f"Current Temp: {temp:.1f}°C | Memory: {[round(t,1) for t in self.past_temps]}")

    def decide(self) -> str:
        """Decide action based on memory (internal model)."""
        if not self.past_temps:
            return OFF
        avg_temp = statistics.mean(self.past_temps)
       
        trend = self.past_temps[-1] - self.past_temps[0] if len(self.past_temps) > 1 else 0


        if trend > TREND_THRESHOLD:
            return COOL + " (Preventive)" if avg_temp > TEMP_MIN else OFF
        elif trend < -TREND_THRESHOLD:
            return HEAT + " (Preventive)" if avg_temp < TEMP_MAX else OFF

        if avg_temp < TEMP_MIN:
            return HEAT
        elif avg_temp > TEMP_MAX:
            return COOL
        else:
            return OFF

def run_simulation(temperature_sequence):
    agent = ThermostatAgent()
    for step, temp in enumerate(temperature_sequence, start=1):
        print(f"\nStep {step}")
        agent.sense(temp)
        action = agent.decide()
        print(f"Action: {action}")
temps = [21.5, 21.8, 22.0, 22.5, 23.0, 23.5, 24.5, 25.0, 24.0, 23.5, 23.0, 22.0, 21.0, 20.5, 19.5]
run_simulation(temps)
