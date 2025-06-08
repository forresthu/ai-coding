import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Wave parameters
v = 2  # wave speed
L = 10.0  # length of the domain
T = 10.0  # total time
nx = 100  # number of spatial points
nt = 200  # number of time steps
dx = L / (nx - 1)  # spatial step size
dt = T / nt  # time step size

# Initialize wave function and velocity
y = np.zeros((nx, nt))
velocity = np.zeros((nx, nt))

# Initial conditions
x = np.linspace(0, L, nx)
for i in range(nx):
    y[i, 0] = np.sin(np.pi * x[i] / L)  # initial displacement
    # Initial velocity (derivative of initial displacement)
    velocity[i, 0] = 0  # starting at rest

# Time-stepping loop to solve the wave equation
for n in range(0, nt - 1):
    for i in range(1, nx - 1):
        # Wave equation: (1/v²)∂²y/∂t² - ∂²y/∂x² = 0
        # Finite difference approximation
        y[i, n + 1] = (2 * y[i, n] - y[i, n - 1] +
                       (v**2 * dt**2 / dx**2) * (y[i + 1, n] - 2 * y[i, n] + y[i - 1, n]))
        
        # Calculate velocity (∂y/∂t)
        if n > 0:
            velocity[i, n] = (y[i, n] - y[i, n - 1]) / dt
    
    # Boundary conditions (fixed ends)
    y[0, n + 1] = 0
    y[-1, n + 1] = 0

# Calculate final velocities
for i in range(1, nx - 1):
    velocity[i, -1] = (y[i, -1] - y[i, -2]) / dt

# Set up the figure with subplots
fig = plt.figure(figsize=(15, 10))

# Create a 2x2 grid of subplots
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], width_ratios=[2, 1])

# Main wave animation plot
ax1 = fig.add_subplot(gs[0, :])
line1, = ax1.plot(x, y[:, 0], 'b-', linewidth=2, label='Wave Displacement')
ax1.set_ylim(-1.5, 1.5)
ax1.set_xlim(0, L)
ax1.set_title('Wave Equation Animation: $(1/v^2)\\frac{\\partial^2 y}{\\partial t^2} - \\frac{\\partial^2 y}{\\partial x^2} = 0$', fontsize=14)
ax1.set_xlabel('Position (x)')
ax1.set_ylabel('Displacement (y)')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Time indicator
time_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, fontsize=12,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# Velocity vs Time plot for a specific point
ax2 = fig.add_subplot(gs[1, 0])
mid_point = nx // 2  # Middle point of the string
time_array = np.linspace(0, T, nt)
line2, = ax2.plot(time_array[:1], velocity[mid_point, :1], 'r-', linewidth=2)
ax2.set_xlim(0, T)
ax2.set_ylim(-2, 2)
ax2.set_title(f'Velocity vs Time at x = {x[mid_point]:.1f}')
ax2.set_xlabel('Time (t)')
ax2.set_ylabel('Velocity (∂y/∂t)')
ax2.grid(True, alpha=0.3)

# Current velocity point
velocity_point, = ax2.plot([], [], 'ro', markersize=8)

# Phase space plot (velocity vs displacement) for the same point
ax3 = fig.add_subplot(gs[1, 1])
line3, = ax3.plot(y[mid_point, :1], velocity[mid_point, :1], 'g-', linewidth=2, alpha=0.7)
ax3.set_xlim(-1.5, 1.5)
ax3.set_ylim(-2, 2)
ax3.set_title('Phase Space\n(Velocity vs Displacement)')
ax3.set_xlabel('Displacement (y)')
ax3.set_ylabel('Velocity (∂y/∂t)')
ax3.grid(True, alpha=0.3)

# Current phase point
phase_point, = ax3.plot([], [], 'go', markersize=8)

# Add parameter text
param_text = fig.text(0.02, 0.02, 
                     f'Parameters:\nWave Speed (v) = {v}\nDomain Length (L) = {L}\n'
                     f'Grid Points (nx) = {nx}\nTime Steps (nt) = {nt}',
                     fontsize=10, verticalalignment='bottom',
                     bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.tight_layout()

# Animation function
def animate(n):
    # Update main wave plot
    line1.set_ydata(y[:, n])
    
    # Update time indicator
    current_time = n * dt
    time_text.set_text(f'Time = {current_time:.2f} s')
    
    # Update velocity vs time plot (show history up to current time)
    line2.set_data(time_array[:n+1], velocity[mid_point, :n+1])
    
    # Update current velocity point
    velocity_point.set_data([current_time], [velocity[mid_point, n]])
    
    # Update phase space plot (show trajectory up to current time)
    line3.set_data(y[mid_point, :n+1], velocity[mid_point, :n+1])
    
    # Update current phase point
    phase_point.set_data([y[mid_point, n]], [velocity[mid_point, n]])
    
    return line1, line2, line3, velocity_point, phase_point, time_text

# Create the animation
ani = animation.FuncAnimation(fig, animate, frames=nt, interval=100, blit=False, repeat=True)

# Add interactive controls
def on_key(event):
    """Handle keyboard events"""
    if event.key == ' ':  # Spacebar to pause/resume
        if ani.running:
            ani.event_source.stop()
            ani.running = False
        else:
            ani.event_source.start()
            ani.running = True
    elif event.key == 'r':  # 'r' to restart
        ani.frame_seq = ani.new_frame_seq()

ani.running = True
fig.canvas.mpl_connect('key_press_event', on_key)

# Show the animation
print("Wave Equation Animation")
print("=" * 30)
print("Controls:")
print("- Spacebar: Pause/Resume")
print("- 'r': Restart animation")
print("- Close window to exit")
print("=" * 30)

plt.show()

# Optional: Save animation as GIF (uncomment to use)
# print("Saving animation as GIF...")
# ani.save('wave_animation.gif', writer='pillow', fps=10)
# print("Animation saved as 'wave_animation.gif'")