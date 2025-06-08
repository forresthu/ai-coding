import numpy as np

def solve_wave_equation(v, x, t):
    """
    Solves the wave equation (1/v^2)d^2y/dt^2 - d^2y/dx^2=0 using finite difference method.

    Parameters:
    v : float
        Wave speed.
    x : numpy.ndarray
        Spatial domain.
    t : numpy.ndarray
        Temporal domain.

    Returns:
    numpy.ndarray
        Wave function values over time and space.
    """
    dx = x[1] - x[0]
    dt = t[1] - t[0]
    c = v * dt / dx

    # Initialize wave function
    y = np.zeros((len(t), len(x)))

    # Initial conditions
    y[0, :] = np.sin(np.pi * x)  # Initial displacement
    y[1, :] = y[0, :]  # Initial velocity is zero

    # Time-stepping loop
    for n in range(1, len(t) - 1):
        for i in range(1, len(x) - 1):
            y[n + 1, i] = (2 * (1 - c**2) * y[n, i] - y[n - 1, i] +
                           c**2 * (y[n, i + 1] + y[n, i - 1]))

    return y