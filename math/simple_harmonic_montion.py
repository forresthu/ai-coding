import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

# Set matplotlib backend with fallback options
import matplotlib
import sys
import os

def setup_matplotlib_backend():
    """Setup matplotlib backend with fallbacks"""
    backends_to_try = ['Qt5Agg', 'TkAgg', 'Agg']
    
    for backend in backends_to_try:
        try:
            matplotlib.use(backend, force=True)
            print(f"Using matplotlib backend: {backend}")
            return backend
        except ImportError as e:
            print(f"Backend {backend} not available: {e}")
            continue
    
    # Default fallback
    print("Using default matplotlib backend")
    return matplotlib.get_backend()

# Setup backend
current_backend = setup_matplotlib_backend()

# Simple Harmonic Motion: -kx = m(d²x/dt²)
# Solution: x(t) = A*cos(ωt + φ) where ω = sqrt(k/m)

class SimpleHarmonicMotionSimulator:
    def __init__(self):
        # Physical parameters
        self.m = 1.0  # mass (kg)
        self.k = 4.0  # spring constant (N/m)
        self.A = 2.0  # amplitude (m)
        self.phi = 0.0  # phase (radians)
        
        # Derived parameters
        self.omega = np.sqrt(self.k / self.m)  # angular frequency
        self.period = 2 * np.pi / self.omega   # period
        self.frequency = 1 / self.period       # frequency
        
        # Time parameters
        self.t_max = 3 * self.period
        self.dt = 0.02
        self.t = np.arange(0, self.t_max, self.dt)
        
        # Calculate position, velocity, and acceleration
        self.x = self.A * np.cos(self.omega * self.t + self.phi)
        self.v = -self.A * self.omega * np.sin(self.omega * self.t + self.phi)
        self.a = -self.A * self.omega**2 * np.cos(self.omega * self.t + self.phi)
        
        # Initialize animation variable
        self.anim = None
        
        # Check if backend supports animation
        self.supports_animation = current_backend not in ['Agg']
        
        # Setup the figure
        self.setup_figure()
        
    def setup_figure(self):
        """Setup the matplotlib figure and subplots"""
        self.fig = plt.figure(figsize=(14, 10))
        self.fig.suptitle('Simple Harmonic Motion: $-kx = m\\frac{d^2x}{dt^2}$', fontsize=16, fontweight='bold')
        
        # Create grid layout
        gs = self.fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], width_ratios=[3, 1])
        
        # Main animation plot
        self.ax_main = self.fig.add_subplot(gs[0, 0])
        self.ax_spring = self.fig.add_subplot(gs[0, 1])
        
        # Position vs time plot
        self.ax_pos = self.fig.add_subplot(gs[1, :])
        
        # Phase space plot (velocity vs position)
        self.ax_phase = self.fig.add_subplot(gs[2, 0])
        
        # Energy plot
        self.ax_energy = self.fig.add_subplot(gs[2, 1])
        
        self.setup_plots()
        
    def setup_plots(self):
        """Setup individual plots"""
        
        # Main animation plot - Mass on spring
        self.ax_main.set_xlim(-0.5, 4)
        self.ax_main.set_ylim(-3, 3)
        self.ax_main.set_xlabel('Position')
        self.ax_main.set_ylabel('Displacement (m)')
        self.ax_main.grid(True, alpha=0.3)
        self.ax_main.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        
        # Draw spring
        spring_x = np.linspace(0, 2, 20)
        spring_y = 0.2 * np.sin(10 * spring_x)
        self.spring_line, = self.ax_main.plot(spring_x, spring_y, 'b-', linewidth=2)
        
        # Mass
        self.mass_point, = self.ax_main.plot([], [], 'ro', markersize=15, label='Mass')
        self.mass_trail, = self.ax_main.plot([], [], 'r-', alpha=0.3, linewidth=1)
        
        # Force vector
        self.force_arrow = self.ax_main.annotate('', xy=(0, 0), xytext=(0, 0),
                                               arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        # Spring visualization (side view)
        self.ax_spring.set_xlim(-0.5, 0.5)
        self.ax_spring.set_ylim(-3, 3)
        self.ax_spring.set_title('Spring-Mass System')
        self.ax_spring.set_ylabel('Position (m)')
        
        # Draw vertical spring
        spring_y = np.linspace(-1, 1, 30)
        spring_x = 0.1 * np.sin(15 * spring_y)
        self.spring_vertical, = self.ax_spring.plot(spring_x, spring_y, 'b-', linewidth=3)
        self.mass_vertical, = self.ax_spring.plot([], [], 'rs', markersize=20)
        
        # Position vs time
        self.ax_pos.set_xlim(0, self.t_max)
        self.ax_pos.set_ylim(-self.A * 1.2, self.A * 1.2)
        self.ax_pos.set_xlabel('Time (s)')
        self.ax_pos.set_ylabel('Position (m)')
        self.ax_pos.grid(True, alpha=0.3)
        
        self.pos_line, = self.ax_pos.plot(self.t, self.x, 'b-', linewidth=2, label='x(t)')
        self.pos_point, = self.ax_pos.plot([], [], 'ro', markersize=8)
        self.ax_pos.legend()
        
        # Phase space plot
        self.ax_phase.set_xlim(-self.A * 1.2, self.A * 1.2)
        self.ax_phase.set_ylim(-self.A * self.omega * 1.2, self.A * self.omega * 1.2)
        self.ax_phase.set_xlabel('Position (m)')
        self.ax_phase.set_ylabel('Velocity (m/s)')
        self.ax_phase.set_title('Phase Space')
        self.ax_phase.grid(True, alpha=0.3)
        
        self.phase_line, = self.ax_phase.plot(self.x, self.v, 'g-', linewidth=2, alpha=0.7)
        self.phase_point, = self.ax_phase.plot([], [], 'ro', markersize=8)
        
        # Energy plot
        self.ax_energy.set_xlim(0, self.t_max)
        kinetic = 0.5 * self.m * self.v**2
        potential = 0.5 * self.k * self.x**2
        total = kinetic + potential
        
        max_energy = np.max(total) * 1.1
        self.ax_energy.set_ylim(0, max_energy)
        self.ax_energy.set_xlabel('Time (s)')
        self.ax_energy.set_ylabel('Energy (J)')
        self.ax_energy.set_title('Energy')
        self.ax_energy.grid(True, alpha=0.3)
        
        self.ke_line, = self.ax_energy.plot(self.t, kinetic, 'r-', linewidth=2, label='Kinetic', alpha=0.7)
        self.pe_line, = self.ax_energy.plot(self.t, potential, 'b-', linewidth=2, label='Potential', alpha=0.7)
        self.te_line, = self.ax_energy.plot(self.t, total, 'k-', linewidth=2, label='Total')
        self.energy_point, = self.ax_energy.plot([], [], 'ro', markersize=6)
        self.ax_energy.legend()
        
        # Add parameter text
        self.param_text = self.fig.text(0.02, 0.95, self.get_param_text(), 
                                       fontsize=10, verticalalignment='top',
                                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
    def get_param_text(self):
        """Get parameter text for display"""
        return f"""Parameters:
m = {self.m:.1f} kg
k = {self.k:.1f} N/m
A = {self.A:.1f} m
ω = {self.omega:.2f} rad/s
T = {self.period:.2f} s
f = {self.frequency:.2f} Hz"""
    
    def animate(self, frame):
        """Animation function"""
        # Current time
        current_t = self.t[frame]
        current_x = self.x[frame]
        current_v = self.v[frame]
        current_a = self.a[frame]
        
        # Update mass position in main plot
        mass_x = 2 + current_x
        self.mass_point.set_data([mass_x], [0])
        
        # Update spring
        spring_x = np.linspace(0, mass_x, 20)
        spring_y = 0.2 * np.sin(10 * np.linspace(0, 2, 20))
        self.spring_line.set_data(spring_x, spring_y)
        
        # Update trail
        trail_length = min(50, frame)
        if trail_length > 0:
            trail_x = 2 + self.x[frame-trail_length:frame+1]
            trail_y = np.zeros(len(trail_x))
            self.mass_trail.set_data(trail_x, trail_y)
        
        # Update force arrow
        force_scale = 0.5
        force_x = current_x * force_scale
        self.force_arrow.xy = (mass_x, 0)
        self.force_arrow.xytext = (mass_x - force_x, 0.5)
        
        # Update vertical spring view
        spring_center = current_x
        spring_y = np.linspace(spring_center - 1, spring_center + 1, 30)
        spring_x = 0.1 * np.sin(15 * (spring_y - spring_center))
        self.spring_vertical.set_data(spring_x, spring_y)
        self.mass_vertical.set_data([0], [current_x])
        
        # Update position point
        self.pos_point.set_data([current_t], [current_x])
        
        # Update phase space point
        self.phase_point.set_data([current_x], [current_v])
        
        # Update energy point
        current_ke = 0.5 * self.m * current_v**2
        self.energy_point.set_data([current_t], [current_ke])
        
        # Update time display
        self.ax_main.set_title(f'Time: {current_t:.2f} s\n'
                              f'x = {current_x:.2f} m, v = {current_v:.2f} m/s, a = {current_a:.2f} m/s²', 
                              fontsize=12)
        
        return (self.mass_point, self.spring_line, self.mass_trail, self.mass_vertical, 
                self.spring_vertical, self.pos_point, self.phase_point, self.energy_point)
    
    def start_animation(self):
        """Start the animation"""
        if not self.supports_animation:
            print(f"Animation not supported with backend '{current_backend}'. Showing static plots instead.")
            self.show_static_plots()
            return None
            
        print("Starting animation... Close the window to stop.")
        
        try:
            self.anim = animation.FuncAnimation(
                self.fig, self.animate, frames=len(self.t),
                interval=50, blit=False, repeat=True
            )
            
            plt.tight_layout()
            plt.show()
            return self.anim
            
        except Exception as e:
            print(f"Animation error: {e}")
            print("Showing static plots instead...")
            self.show_static_plots()
            return None
    
    def show_static_plots(self):
        """Show static plots if animation fails"""
        plt.close('all')  # Close any existing figures
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Simple Harmonic Motion - Static Analysis', fontsize=16)
        
        # Position vs time
        ax1.plot(self.t, self.x, 'b-', linewidth=2)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Position (m)')
        ax1.set_title('Position vs Time')
        ax1.grid(True, alpha=0.3)
        
        # Phase space
        ax2.plot(self.x, self.v, 'r-', linewidth=2)
        ax2.set_xlabel('Position (m)')
        ax2.set_ylabel('Velocity (m/s)')
        ax2.set_title('Phase Space')
        ax2.grid(True, alpha=0.3)
        
        # Energy
        kinetic = 0.5 * self.m * self.v**2
        potential = 0.5 * self.k * self.x**2
        total = kinetic + potential
        
        ax3.plot(self.t, kinetic, 'r-', linewidth=2, label='Kinetic')
        ax3.plot(self.t, potential, 'b-', linewidth=2, label='Potential')
        ax3.plot(self.t, total, 'k-', linewidth=2, label='Total')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Energy (J)')
        ax3.set_title('Energy vs Time')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Acceleration vs time
        ax4.plot(self.t, self.a, 'g-', linewidth=2)
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Acceleration (m/s²)')
        ax4.set_title('Acceleration vs Time')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot to file as backup
        try:
            filename = 'simple_harmonic_motion.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Plot saved as '{filename}'")
        except Exception as e:
            print(f"Could not save plot: {e}")
        
        plt.show()

def create_simple_plots():
    """Create simple plots without interactive widgets"""
    # Physical parameters
    m = 1.0  # mass (kg)
    k = 4.0  # spring constant (N/m)
    A = 2.0  # amplitude (m)
    phi = 0.0  # phase (radians)
    
    # Derived parameters
    omega = np.sqrt(k / m)  # angular frequency
    period = 2 * np.pi / omega   # period
    
    # Time parameters
    t_max = 3 * period
    t = np.linspace(0, t_max, 1000)
    
    # Calculate position, velocity, and acceleration
    x = A * np.cos(omega * t + phi)
    v = -A * omega * np.sin(omega * t + phi)
    a = -A * omega**2 * np.cos(omega * t + phi)
    
    # Create plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Simple Harmonic Motion Analysis', fontsize=16)
    
    # Position vs time
    ax1.plot(t, x, 'b-', linewidth=2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Position (m)')
    ax1.set_title('Position vs Time')
    ax1.grid(True, alpha=0.3)
    
    # Velocity vs time
    ax2.plot(t, v, 'r-', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Velocity (m/s)')
    ax2.set_title('Velocity vs Time')
    ax2.grid(True, alpha=0.3)
    
    # Phase space
    ax3.plot(x, v, 'g-', linewidth=2)
    ax3.set_xlabel('Position (m)')
    ax3.set_ylabel('Velocity (m/s)')
    ax3.set_title('Phase Space')
    ax3.grid(True, alpha=0.3)
    
    # Energy
    kinetic = 0.5 * m * v**2
    potential = 0.5 * k * x**2
    total = kinetic + potential
    
    ax4.plot(t, kinetic, 'r-', linewidth=2, label='Kinetic')
    ax4.plot(t, potential, 'b-', linewidth=2, label='Potential')
    ax4.plot(t, total, 'k-', linewidth=2, label='Total')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Energy (J)')
    ax4.set_title('Energy vs Time')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    try:
        filename = 'simple_harmonic_motion_simple.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Plot saved as '{filename}'")
    except Exception as e:
        print(f"Could not save plot: {e}")
    
    plt.show()

def main():
    """Main function with improved error handling"""
    print("Simple Harmonic Motion Simulator")
    print("=" * 40)
    print("Differential Equation: -kx = m(d²x/dt²)")
    print("Solution: x(t) = A*cos(ωt + φ) where ω = √(k/m)")
    print(f"Current backend: {current_backend}")
    print("=" * 40)
    
    try:
        if current_backend == 'Agg':
            print("Note: Using non-interactive backend. Only static plots available.")
            choice = input("Choose simulation type:\n1. Static plots (full simulator)\n2. Simple plots\nEnter choice (1 or 2): ")
        else:
            choice = input("Choose simulation type:\n1. Animated simulation\n2. Static plots (full simulator)\n3. Simple plots\nEnter choice (1, 2, or 3): ")
        
        if choice == "1":
            if current_backend == 'Agg':
                print("\nShowing static plots...")
                sim = SimpleHarmonicMotionSimulator()
                sim.show_static_plots()
            else:
                print("\nStarting animated simulation...")
                sim = SimpleHarmonicMotionSimulator()
                anim = sim.start_animation()
                
                # Keep reference to animation to prevent garbage collection
                if anim:
                    input("Press Enter to exit...")
                    
        elif choice == "2":
            print("\nShowing static plots...")
            sim = SimpleHarmonicMotionSimulator()
            sim.show_static_plots()
            
        elif choice == "3":
            print("\nShowing simple plots...")
            create_simple_plots()
            
        else:
            print("Invalid choice. Showing simple plots...")
            create_simple_plots()
            
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        print("Falling back to simple plots...")
        create_simple_plots()

if __name__ == "__main__":
    main()