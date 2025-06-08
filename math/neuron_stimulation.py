import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Time settings
dt = 0.1  # ms
T = 50    # total time in ms
time = np.arange(0, T, dt)

# Neuron parameters
tau_m = 10.0         # membrane time constant (ms)
V_rest = -70.0       # resting potential (mV)
V_th = -50.0         # threshold potential (mV)
V_reset = -65.0      # reset potential after spike (mV)
R = 30.0              # membrane resistance (MΩ)

# Stimulus: series of increasing depolarizing pulses
I = np.zeros_like(time)
pulse_starts = np.arange(5, 45, 5)  # start times of pulses
pulse_duration = 2                 # ms
amplitudes = np.linspace(1.0, 6.0, len(pulse_starts))

for start, amp in zip(pulse_starts, amplitudes):
    idx = (time >= start) & (time < start + pulse_duration)
    I[idx] = amp

# Membrane potential initialization
V = np.zeros_like(time)
V[0] = V_rest
spikes = []

# Simulate using LIF model with refractory period
refractory_steps = int(15 / dt)
refrac_until = -1  # index until which neuron is refractory

for t in range(1, len(time)):
    if t <= refrac_until:
        V[t] = V_reset
        continue
    dV = (-(V[t-1] - V_rest) + R * I[t]) * (dt / tau_m)
    V[t] = V[t-1] + dV
    if V[t] >= V_th:
        V[t] = 60  # simulate spike peak
        spikes.append(t)
        refrac_until = min(t + refractory_steps, len(time) - 1)

# Create animation with proper display
fig, ax = plt.subplots(figsize=(12, 6))

# Initialize empty lines
line1, = ax.plot([], [], lw=2, label='Membrane Potential (mV)', color='blue')
line2, = ax.plot([], [], lw=2, label='Stimulus Current (scaled)', color='red')
threshold_line = ax.axhline(V_th, color='orange', linestyle='--', linewidth=2, label='Threshold')

# Set plot properties
ax.set_xlim(0, T)
ax.set_ylim(-80, 80)
ax.set_xlabel('Time (ms)', fontsize=12)
ax.set_ylabel('Voltage (mV) / Current (scaled)', fontsize=12)
ax.legend(loc='upper right')
ax.set_title("LIF Neuron Simulation with Stimulus", fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

# Add parameter text
param_text = ax.text(0.02, 0.98, 
                    f'τ_m = {tau_m} ms\nV_rest = {V_rest} mV\nV_th = {V_th} mV\nV_reset = {V_reset} mV',
                    transform=ax.transAxes, fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Time indicator
time_text = ax.text(0.02, 0.02, '', transform=ax.transAxes, fontsize=12,
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

# Animation function
def animate(i):
    """Animation function - called sequentially"""
    idx = min(i, len(time) - 1)  # Ensure we don't go out of bounds
    
    # Update membrane potential line
    line1.set_data(time[:idx+1], V[:idx+1])
    
    # Update stimulus current line (scaled for visualization)
    line2.set_data(time[:idx+1], I[:idx+1] * 10 - 70)
    
    # Update time indicator
    current_time = time[idx]
    time_text.set_text(f'Time: {current_time:.1f} ms')
    
    # Count spikes up to current time
    spike_count = len([s for s in spikes if s <= idx])
    if spike_count > 0:
        ax.set_title(f"LIF Neuron Simulation - Spikes: {spike_count}", fontsize=14, fontweight='bold')
    
    return line1, line2, time_text

# Create and start animation
print("Starting LIF Neuron Animation...")
print("=" * 40)
print(f"Simulation parameters:")
print(f"- Duration: {T} ms")
print(f"- Time step: {dt} ms")
print(f"- Membrane time constant: {tau_m} ms")
print(f"- Threshold: {V_th} mV")
print("=" * 40)

ani = animation.FuncAnimation(
    fig, animate, 
    frames=len(time),
    interval=50,  # 50ms between frames for smooth animation
    blit=False,   # Set to False for better compatibility
    repeat=True
)

# Show the plot (don't close it!)
plt.tight_layout()
plt.show()

# Optional: Save as GIF (uncomment to use)
print("Saving animation...")
ani.save('lif_neuron_animation.gif', writer='pillow', fps=20)
print("Animation saved as 'lif_neuron_animation.gif'")