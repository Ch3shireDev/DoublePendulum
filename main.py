

# comment these lines if you want interactive mode,
# i.e., if you want to see the animation in real time.
import matplotlib
# matplotlib.use('Agg')


import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.integrate import ode


def equations(t, y, args):
    """ the equations for the double pendulum """
    x1 = y[0]  # x1 = theta1, angle
    x2 = y[1]  # x2 = theta2, angle
    p1 = y[2]  # p1 = omega1, angular velocity
    p2 = y[3]  # p2 = omega2, angular velocity
    l1, l2, m1, m2, g = args
    x1_eq = p1
    x2_eq = p2
    p1_eq = -((g*(2*m1+m2)*np.sin(x1)+m2*(g*np.sin(x1-2*x2)+2*(l2*p2**2+l1*p1 **
                                                               2*np.cos(x1-x2))*np.sin(x1-x2)))/(2*l1*(m1+m2-m2*(np.cos(x1-x2))**2)))
    p2_eq = ((l1*(m1+m2)*p1**2+g*(m1+m2)*np.cos(x1)+l2*m2*p2**2 *
              np.cos(x1-x2))*np.sin(x1-x2))/(l2*(m1+m2-m2*(np.cos(x1-x2))**2))
    return [x1_eq, x2_eq, p1_eq, p2_eq]


def calculate_trajectory(args, time, y0):
    """ uses scipy's ode itegrator to simulate the equations """
    t0, t1, dt = time
    r = ode(equations).set_integrator('dopri5')
    r.set_initial_value(y0, t0).set_f_params(args)
    data = [[t0, y0[0], y0[1], y0[2], y0[3]]]
    while r.successful() and r.t < t1:
        r.integrate(r.t+dt)
        data.append([r.t, r.y[0], r.y[1], r.y[2], r.y[3]])
    return np.array(data)


def from_angle_to_xy(args, angles):
    """ converts angles into xy positions """
    l1, l2, m1, m2, g = args
    time, theta1, theta2 = angles.T
    x1 = l1*np.sin(theta1)
    y1 = -l1*np.cos(theta1)
    x2 = l2*np.sin(theta2) + x1
    y2 = -l2*np.cos(theta2) + y1
    return np.array([time, x1, y1, x2, y2]).T


l1 = 0.5  # length of arms
l2 = 0.5
m1 = 1.0  # mass of the pendulum
m2 = 1.0
g = 10.0  # acceleration of gravity
args = [l1, l2, m1, m2, g]
fps = 80
total_time = 5  # seconds
time = [0.0, total_time, 1.0/fps]  # start, finish, dt
ic = [np.pi*0.65, np.pi*1.1, 0.0, 0.0]

# here the magic happens
d = calculate_trajectory(args, time, ic)
data_TXY = from_angle_to_xy(args, d[:, :3])


# let's plot stuff, and make a nice movie
make_movie = False
params = {'backend': 'ps',
          'font.size': 20,
          'font.family': 'serif',
          # Times, Palatino, New Century Schoolbook, Bookman, Computer Modern Roman
          'font.serif': ['Computer Modern Roman'],
          'ps.usedistiller': 'xpdf',
          'text.usetex': True,
          }
plt.rcParams.update(params)
plt.ion()
fig = plt.figure(figsize=(9.6, 5.4), dpi=100)  # 1920x1080
fig.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0.02, wspace=0.02)
ax = fig.add_subplot(111)
ax.axis('off')  # no frame


def plot_last_seconds(data, index):
    """ Plots a line with the trajectory of the tip of pendulum 2 (x2,y2)
    """
    how_long = 0.1  # seconds
    n = int(how_long/time[2])
    to_plot = data[:index, :]
    if index < n:
        prepend = np.tile(data[0], (n-index, 1))
        to_plot = np.vstack([prepend, to_plot])
        index = n
    colormap = plt.cm.Greys_r
    colors = [colormap(i) for i in np.linspace(0.0, 1.0, n-1)]
    plots = []
    for j in np.arange(n-1):
        p, = ax.plot(to_plot[index-j-1:index-j+1, 3], to_plot[index-j-1:index-j+1, 4],
                     color=colors[j], zorder=-1)
        plots.append(p)
    return plots


# "plot" returns a tuple of line objects, thus the comma
t, x1, y1, x2, y2 = data_TXY[0]
line1, = ax.plot([0.0, x1], [0.0, y1], 'r-')
line2, = ax.plot([x1, x2], [y1, y2], 'r-')
circ1, = ax.plot([x1], [y1], 'ro', markersize=10)
circ2, = ax.plot([x2], [y2], 'ro', markersize=10)
sizeY = 1.2
ax.axis([-sizeY*16/9, sizeY*16/9, -sizeY, sizeY])

frame_names = []
tex = ax.text(0.0, 0.85, '', ha="center")

for i, v in enumerate(data_TXY):
    t, x1, y1, x2, y2 = v
    # print("t={:.2f}".format(t)) # you might want to know how things are going...
    line1.set_data([0.0, x1], [0.0, y1])
    line2.set_data([x1, x2], [y1, y2])
    circ1.set_data([x1], [y1])
    circ2.set_data([x2], [y2])

    # # plot_last_seconds considerably slows down the simulation,
    # # but makes it much prettier...
    pls = plot_last_seconds(data_TXY, i+1)
    tex.set_text(r"$t={:.3f}$ s".format(t))
    fig.canvas.draw()
    # if make_movie:
    #     fname = "_tmp{:05d}.png".format(i)
    #     frame_names.append(fname)
    #     fig.savefig(fname,bbox_inches='tight')
    # for k in pls:
    #     k.remove()

if make_movie:
    frames = "_tmp%5d.png"
    movie_command = "ffmpeg -y -r {:} -i {:} double.mp4".format(fps, frames)
    os.system(movie_command)

    for fname in frame_names:
        os.remove(fname)
