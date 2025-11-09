import torch
import matplotlib.pyplot as plt
from IPython.display import clear_output
import time


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


def plot_data_advanced(distances, times, normalize=False):
    plt.figure(figsize=(8, 6))
    plt.plot(distances, times, color='orange', marker='o', linestyle='none', label='Actual Delivery Times')
    if normalize:
        plt.title('Normalize Delivery Data (Bikes & Cars)')
        plt.xlabel('Normalized Distance')
        plt.ylabel('Normalized Time')
        plt.legend()
        plt.grid(True)
        plt.show()
    else:
        plt.title('Delivery Data (Bikes & Cars)')
        plt.xlabel('Distance (miles)')
        plt.ylabel('Time (minutes)')
        plt.legend()
        plt.grid(True)
        plt.show()

def plot_final_fit(model, distances, times, distances_norm, time_std, times_mean):
    model.eval()
    with torch.no_grad():
        predicted_norm = model(distances_norm)
    predicted_times = (predicted_norm * time_std) + times_mean
    plt.figure(figsize=(8, 6))
    plt.plot(distances, times, color='orange', marker='o', 
             linestyle='none', label='Actual Delivery Times')
    
    plt.plot(distances, predicted_times, color='green', marker='o', 
             linestyle='none', label='Predicted Delivery Times')
    plt.title('Non-Linear Model Fit vs Actual Data')
    plt.xlabel('Distance (miles)')
    plt.ylabel('Time (minutes)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_training_progress(epoch, loss, model, distances_norm, times_norm):
    clear_output(wait=True) # removes exisitin plot in the output if there is any
    predicted_norm = model(distances_norm)
    x_plot = distances_norm
    y_plot = times_norm

    y_pred_plot = predicted_norm.detach().numpy()
    sorted_indices = x_plot.argsort(axis=0).flatten()

    plt.figure(figsize=(8, 6))
    plt.plot(x_plot, y_plot, color='orange', marker='o', linestyle='none', label='Actual Delivery Times')
    plt.plot(x_plot[sorted_indices], y_pred_plot[sorted_indices], color='green', marker='o', linestyle='none', label='Predicted Delivery Times')
    plt.title(f'Epoch {epoch + 1}, Loss: {loss:.4f}')

    plt.xlabel('Normalized Distance')
    plt.ylabel('Normalized Time')
    plt.legend()
    plt.grid(True)
    plt.show()

    time.sleep(0.5)