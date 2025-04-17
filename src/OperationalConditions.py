from typing import List
from pathlib import Path

class OperationalCondition:
    def __init__(self, wind_speed: float, pitch: float, rpm: float, aero_power: float, aero_thrust: float):
        self.wind_speed = wind_speed
        self.pitch = pitch
        self.rpm = rpm
        self.aero_power = aero_power
        self.aero_thrust = aero_thrust

    def __repr__(self):
        return (f"OperationalCondition(wind_speed={self.wind_speed}, pitch={self.pitch}, "
                f"rpm={self.rpm}, aero_power={self.aero_power}, aero_thrust={self.aero_thrust})")


class OperationalConditions:
    def __init__(self, conditions: List[OperationalCondition] = None):
        self.conditions = conditions if conditions else []

    def load_from_file(self, file_path: Path):
        lines = file_path.read_text(encoding='utf-8').splitlines()
        self.conditions = []

        for line in lines:
            line = line.strip()
            if not line or any(line.startswith(c) for c in ("-", "=", "!", "#")):
                continue

            parts = line.split()
            if len(parts) != 5:
                continue  # skip malformed lines

            try:
                wind_speed = float(parts[0])
                pitch = float(parts[1])
                rpm = float(parts[2])
                aero_power = float(parts[3])
                aero_thrust = float(parts[4])

                condition = OperationalCondition(
                    wind_speed=wind_speed,
                    pitch=pitch,
                    rpm=rpm,
                    aero_power=aero_power,
                    aero_thrust=aero_thrust
                )
                self.conditions.append(condition)
            except ValueError:
                continue

    def __repr__(self):
        return f"OperationalConditions(num_conditions={len(self.conditions)})"
