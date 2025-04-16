from dataclasses import dataclass, field
from typing import List
from pathlib import Path

@dataclass
class OperationalCondition:
    wind_speed: float
    pitch: float
    rpm: float
    aero_power: float
    aero_thrust: float

@dataclass
class OperationalConditions:
    conditions: List[OperationalCondition] = field(default_factory=list)

    @classmethod
    def from_file(cls, file_path: Path) -> "OperationalConditions":
        lines = file_path.read_text(encoding='utf-8').splitlines()
        conditions = []

        for line in lines:
            line = line.strip()
            if not line or any(line.startswith(c) for c in ("-", "=", "!", "#")):
                continue

            parts = line.split()
            if len(parts) != 5:
                continue  # skip malformed lines

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
            conditions.append(condition)

        return cls(conditions=conditions)

    def __repr__(self):
        return f"OperationalConditions(num_conditions={len(self.conditions)})"
