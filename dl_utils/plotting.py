import torch
import matplotlib.pyplot as plt


def plot_results(model, distances, times):
    model.eval()
    with torch.no_grad():
        predicted_times = model(distances)
    
    plt.figure(figsize=(8, 6))
    plt.plot(distances, times, color='orange', marker='o', linestyle='None', label='Actual Delivery Times')
    plt.plot(distances, predicted_times, color='green', marker='o', linestyle='None', label='Predicted Delivery Times')
    plt.title('Actual vs Predicted Delivery Times')
    plt.xlabel('Distance (km)')
    plt.ylabel('Time (minutes)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_nonlinear_comparison(model, new_distances, new_times):
    model.eval()
    with torch.no_grad():
        predicted_times = model(new_distances)
    
    plt.figure(figsize=(8, 6))
    plt.plot(new_distances, new_times, color='orange', marker='o', linestyle='None', label='Actual Delivery Times')
    plt.plot(new_distances, predicted_times, color='green', marker='o', linestyle='None', label='Linear Model Predictions')
    plt.title('Actual vs Linear Model Predictions')
    plt.xlabel('Distance (km)')
    plt.ylabel('Time (minutes)')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.show()
