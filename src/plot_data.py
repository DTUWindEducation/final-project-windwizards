import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def load_and_parse_data(file_path):
    df = pd.read_csv(file_path, parse_dates=["Time"])
    return df

def plot_temperature(df, output_path=None):
    plt.figure(figsize=(12, 6))
    plt.plot(df["Time"], df["temperature_2m"], label="Temperature [°F]", color="red")
    plt.xlabel("Time [h]")
    plt.ylabel("Temperature [°F]")
    plt.title("Temperature Over Time")
    plt.legend()
    plt.grid(True)
    
    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()

def plot_power(df, output_path=None):
    plt.figure(figsize=(12, 6))
    plt.plot(df["Time"], df["Power"], label="Normalized Power Output", linestyle="--", color="blue")
    plt.xlabel("Time [h]")
    plt.ylabel("Power Output Normalized")
    plt.title("Normalized Power Output Over Time")
    plt.legend()
    plt.grid(True)
    
    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()

def main():
    # Absolute path to the dataset, relative to this script's location
    file_path = Path(__file__).resolve().parent / ".." / "inputs" / "Location1.csv"
    file_path = file_path.resolve()  # convert to full absolute path
    
    df = load_and_parse_data(file_path)  
    plot_temperature(df)
    plot_power(df)

if __name__ == "__main__":
    main()