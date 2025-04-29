from typing import List
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

class OperationalCharacteristic:
    def __init__(self, wind_speed: float, pitch: float, rpm: float, aero_power: float, aero_thrust: float, rho: float = 1.225):
        self.wind_speed = wind_speed
        self.pitch = pitch
        self.rpm = rpm
        self.aero_power = aero_power
        self.aero_thrust = aero_thrust
        self.rho = rho
        self.omega = rpm * 2 * np.pi / 60  # Convert RPM to rad/s

    def __repr__(self):
        return (f"OperationalCharacteristic(wind_speed={self.wind_speed}, pitch={self.pitch}, "
                f"rpm={self.rpm}, aero_power={self.aero_power}, aero_thrust={self.aero_thrust})")


class OperationalCharacteristics:
    def __init__(self, characteristics: List[OperationalCharacteristic] = None):
        self.characteristics = characteristics if characteristics else []

    def load_from_file(self, file_path: Path):
        lines = file_path.read_text(encoding='utf-8').splitlines()
        self.characteristics = []

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

                condition = OperationalCharacteristic(
                    wind_speed=wind_speed,
                    pitch=pitch,
                    rpm=rpm,
                    aero_power=aero_power,
                    aero_thrust=aero_thrust
                )
                self.characteristics.append(condition)
            except ValueError:
                continue

    def plot_characteristics(self, V_min: float = 0, V_max: float = 30, num_points: int = 100):
        """Compute optimal operational strategy, i.e.,  blade pitch angle theta_p
        and rotational speed omega, as function of wind speed V_0, based on 
        the provided operational strategy"""
        V = np.linspace(V_min, V_max, num_points)
        theta_p = np.zeros(num_points)
        omega = np.zeros(num_points)

        for i, wind_speed in enumerate(V):
            # Find the closest operational characteristic
            closest_condition = min(self.characteristics, key=lambda x: abs(x.wind_speed - wind_speed))
            theta_p[i] = closest_condition.pitch
            omega[i] = closest_condition.omega

        plt.figure(figsize=(10, 6))
        plt.plot(V, theta_p, label='Pitch Angle (degrees)', color='blue')
        plt.plot(V, omega, label='Angular Velocity (rad/s)', color='red')
        plt.xlabel('Wind Speed (m/s)')
        plt.ylabel('Operational Characteristics')
        plt.title('Operational Characteristics vs Wind Speed')
        plt.legend()
        plt.grid()
        plt.show()


    def __repr__(self):
        return f"OperationalCharacteristics(num_conditions={len(self.characteristics)})."
