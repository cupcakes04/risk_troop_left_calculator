import random
from collections import Counter
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog
import matplotlib
matplotlib.use('Agg')  # Add this near the top
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def roll_dice(num_dice):
    """Simulate rolling `num_dice` dice."""
    return sorted([random.randint(1, 6) for _ in range(num_dice)], reverse=True)


def compute_losses(attacker_rolls, defender_rolls):
    """
    Compute losses for a single round of battle.
    - `attacker_rolls`: Sorted list of attack dice rolls.
    - `defender_rolls`: Sorted list of defense dice rolls.
    """
    attacker_losses = 0
    defender_losses = 0

    for a_roll, d_roll in zip(attacker_rolls, defender_rolls):
        if a_roll > d_roll:
            defender_losses += 1
        else:
            attacker_losses += 1

    return attacker_losses, defender_losses


def plot_distribution(loss_probs, title, color, axe):
    """
    Plot a distribution of troop losses on the provided Axes object.
    - `loss_probs`: Dictionary mapping losses to probabilities.
    - `title`: Title of the plot.
    - `color`: Color of the bars.
    - `axe`: Matplotlib Axes object to draw the plot.
    """
    losses = list(loss_probs.keys())
    probabilities = list(loss_probs.values())

    # Dynamically adjust step size for ticks
    step = 1 if max(losses) < 10 else int(max(losses) / 10)

    # Plot on the provided Axes object
    axe.bar(losses, probabilities, color=color, alpha=0.7)
    axe.set_xlabel("Troop Losses")
    axe.set_ylabel("Probability")
    axe.set_title(title)
    axe.set_xticks(range(min(losses), max(losses) + 1, step))
    axe.grid(axis="y", linestyle="--", alpha=0.7)


def create_plot_window(fig):
    plot_window = tk.Toplevel()
    plot_window.title("Battle Results")
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    return plot_window


def submit_form():
    """Handle the form submission and run the battle simulation."""
    # Get all input values from the form
    attacker_troops = int(attacker_troops_entry.get())
    defender_troops = int(defender_troops_entry.get())
    num_trials = int(num_trials_entry.get()) if num_trials_entry.get() else 100000
    capital = capital_var.get() == 'yes'
    attacker_dice = int(attacker_dice_entry.get()) if attacker_dice_entry.get() else 3
    defender_dice = int(defender_dice_entry.get()) if defender_dice_entry.get() else 2

    # Run the battle simulation
    results = simulate_battle(attacker_troops, defender_troops, capital, num_trials, attacker_dice, defender_dice)

    # # Display the results in a label
    # result_text.set(f"Attacker Win Rate: {results['attacker_win_rate'] * 100:.2f}%\n"
    #                 f"Defender Win Rate: {results['defender_win_rate'] * 100:.2f}%")

    # # Show the results window
    # results_window.deiconify()  # Show the results window


def simulate_battle(attacker_troops, defender_troops, capital=False, num_trials=100000, attacker_dice=3, defender_dice=2):
    """
    Simulate multiple battles and calculate win rate and troop loss distributions.
    - `attacker_dice`: Max dice attacker can roll.
    - `defender_dice`: Max dice defender can roll.
    - `capital`: Capital or not.
    - `attacker_troops`: Initial number of troops for the attacker.
    - `defender_troops`: Initial number of troops for the defender.
    - `num_trials`: Number of simulations to run.
    """
    attacker_wins = 0
    defender_wins = 0
    attacker_loss_dist = Counter()
    defender_loss_dist = Counter()
    if capital: defender_dice = 3

    print("Simulating battles...")
    for _ in range(num_trials):
        atk_remaining, def_remaining = attacker_troops, defender_troops

        while atk_remaining > 1 and def_remaining > 0:
            # Determine the number of dice rolled by each side
            atk_rolls = min(attacker_dice, atk_remaining - 1)
            def_rolls = min(defender_dice, def_remaining)

            # Roll dice and compute losses
            attacker_rolls = roll_dice(atk_rolls)
            defender_rolls = roll_dice(def_rolls)
            atk_losses, def_losses = compute_losses(attacker_rolls, defender_rolls)

            # Update troop counts
            atk_remaining -= atk_losses
            def_remaining -= def_losses

        # Determine winner
        if atk_remaining > 1:
            attacker_wins += 1
            attacker_loss_dist[attacker_troops - atk_remaining] += 1
        else:
            defender_wins += 1
            defender_loss_dist[defender_troops - def_remaining] += 1

    # Normalize distributions
    total_simulations = attacker_wins + defender_wins
    attacker_loss_probs = {k: v / attacker_wins for k, v in attacker_loss_dist.items()} if attacker_wins > 0 else {}
    defender_loss_probs = {k: v / defender_wins for k, v in defender_loss_dist.items()} if defender_wins > 0 else {}

    # Plot probability distributions
    attacker_win_rate = attacker_wins / total_simulations
    defender_win_rate = defender_wins / total_simulations
    print("\nResults:")
    print(f"Attacker Win Rate: {attacker_win_rate:.2%}")
    print(f"Defender Win Rate: {defender_win_rate:.2%}")
    
    # Consolidate Plotting in One Window
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    if attacker_loss_probs:
        plot_distribution(loss_probs=attacker_loss_probs, title=f"Attacker Troop Loss Distribution (WR: {attacker_win_rate:.2%})", color="red", axe=axes[0])
    if defender_loss_probs:
        plot_distribution(loss_probs=defender_loss_probs, title=f"Defender Troop Loss Distribution (WR: {defender_win_rate:.2%})", color="blue", axe=axes[1])

    plt.tight_layout()
    create_plot_window(fig)
    
    return {
        "attacker_win_rate": attacker_win_rate,
        "defender_win_rate": defender_win_rate,
        "attacker_loss_probs": attacker_loss_probs,
        "defender_loss_probs": defender_loss_probs,
    }


# Main GUI
root = tk.Tk()
root.title("Risk Troop Losses Simulator (TR)")

# Labels and Entry Widgets for user inputs
tk.Label(root, text="Enter the number of attacker troops:").grid(row=0, column=0)
attacker_troops_entry = tk.Entry(root)
attacker_troops_entry.grid(row=0, column=1)

tk.Label(root, text="Enter the number of defender troops:").grid(row=1, column=0)
defender_troops_entry = tk.Entry(root)
defender_troops_entry.grid(row=1, column=1)

tk.Label(root, text="Enter the number of trials (default 100000):").grid(row=2, column=0)
num_trials_entry = tk.Entry(root)
num_trials_entry.grid(row=2, column=1)

tk.Label(root, text="Is this a capital (yes/no, default no):").grid(row=3, column=0)
capital_var = tk.Entry(root)
capital_var.grid(row=3, column=1)

tk.Label(root, text="Enter the number of dice for attacker (default 3):").grid(row=4, column=0)
attacker_dice_entry = tk.Entry(root)
attacker_dice_entry.grid(row=4, column=1)

tk.Label(root, text="Enter the number of dice for defender (default 2):").grid(row=5, column=0)
defender_dice_entry = tk.Entry(root)
defender_dice_entry.grid(row=5, column=1)

# Submit button to start the simulation
submit_button = tk.Button(root, text="Submit", command=submit_form)
submit_button.grid(row=6, column=0, columnspan=2)

# # Results window
# results_window = tk.Toplevel(root)
# results_window.title("Simulation Results")
# results_window.withdraw()  # Hide the window initially

# result_text = tk.StringVar()
# result_label = tk.Label(results_window, textvariable=result_text)
# result_label.pack()

# Start the GUI main loop
root.mainloop()