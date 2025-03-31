import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def load_and_parse_data(file_path):
    df = pd.read_csv(file_path, parse_dates=["Time"])
    return df

def plot_data(df, output_path=None):
    plt.figure(figsize=(12, 6))
    plt.plot(df["Time"], df["temperature_2m"], label="Temperature (°C)")
    plt.plot(df["Time"], df["Power"], label="Power Output", linestyle="--")
    plt.xlabel("Time")
    plt.ylabel("Values")
    plt.title("Temperature and Power Over Time")
    plt.legend()
    plt.grid(True)

    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()

def main():
    # Get the absolute path to the dataset, relative to this script's location
    file_path = Path(__file__).resolve().parent / ".." / "inputs" / "Location1.csv"
    file_path = file_path.resolve()  # convert to full absolute path
    
    df = load_and_parse_data(file_path)  # ✅ load data first
    plot_data(df)  # ✅ now pass the DataFrame


if __name__ == "__main__":
    main()
