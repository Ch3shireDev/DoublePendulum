from numpy import sin, cos
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

dt = 1./100  # 30 fps

L = 70

sun_size = 100
earth_size = 10

fig = plt.figure(figsize=(20,10), dpi=70)
ax = fig.add_subplot(111, aspect='equal', autoscale_on=True,
                     xlim=(-L*2, L*2), ylim=(-L, L),)

ax.grid()
ax.axis('off')

sunplot, = ax.plot([], [], 'o-', lw=5, color='#bbaa00', markersize=sun_size)
earthplot, = ax.plot([], [], 'o-', lw=5, color='#0000aa', markersize=earth_size)
line, = ax.plot([], [], '-', lw=1, color='blue')


def refresh_plots():
    global sunplot,earthplot,line
    # ax.cla()
    sunplot.remove()
    earthplot.remove()
    sunplot, = ax.plot([], [], 'o-', lw=5, color='#bbaa00', markersize=sun_size)
    earthplot, = ax.plot([], [], 'o-', lw=5, color='#0000aa', markersize=earth_size)
    line, = ax.plot([], [], '-', lw=1, color='blue')

refresh_plots()

x0, y0 = 0, 0
x1, y1 = 50, 0

vx, vy = 0, 140


axvelocity = plt.axes([0.1,0.1,0.8,0.03])
svelocity = Slider(axvelocity, 'Velocity', 0.1, 500.0, valinit=vy)


def init():
    """initialize animation"""
    sunplot.set_data([], [])
    earthplot.set_data([], [])
    line.set_data([], [])
    return sunplot, earthplot



trajectory_x = []
trajectory_y = []


def animate(i):
    global x1, y1, vx, vy
    if not pause:
        v1 = np.array((x0, y0))
        v2 = np.array((x1, y1))
        vnorm = (v2-v1) / np.linalg.norm(v2-v1)

        F = -1000000*vnorm/np.linalg.norm(v1-v2)**2

        vx += F[0]*dt
        vy += F[1]*dt

        v = np.array([vx,vy])
        v = np.linalg.norm(v)
        svelocity.set_val(v)

        x1 += vx*dt
        y1 += vy*dt

        X0 = [x0]
        Y0 = [y0]

        X1 = [x1]
        Y1 = [y1]

        trajectory_x.append(x1)
        trajectory_y.append(y1)

        # if len(trajectory_x) > 128:
        #     trajectory_x.pop(0)
        #     trajectory_y.pop(0)


    sunplot.set_data([x0], [y0])
    earthplot.set_data([x1], [y1])
    line.set_data(trajectory_x, trajectory_y)
    return sunplot, earthplot, line


pause = False
grabbed = False

def onPress(event):
    global pause, grabbed
    pause = True
    mousePos = np.array([event.xdata, event.ydata])
    if np.linalg.norm(mousePos - np.array((x0,y0))) < 10:
        grabbed = True
    
def onRelease(event):
    global pause, grabbed
    pause = False
    grabbed = False

def onMouseMove(event):
    global x0,y0
    if not grabbed:
        return
    x0,y0 = event.xdata, event.ydata
    
def onDialChange(value):
    global vx, vy
    v = np.array([vx,vy])
    v /= np.linalg.norm(v)
    v *= value
    vx, vy = v

def onScrollEvent(event):
    global L, ax,sun_size,earth_size
    if event.button == 'up':
        L*=1.1
        sun_size /= 1.1
        earth_size /= 1.1
    else:
        L/=1.1
        sun_size*=1.1
        earth_size*=1.1

    ax.set_xlim([-2*L, 2*L])
    ax.set_ylim([-L, L])
    refresh_plots()

fig.canvas.mpl_connect('button_press_event', onPress)
fig.canvas.mpl_connect('button_release_event', onRelease)
fig.canvas.mpl_connect('motion_notify_event', onMouseMove)
fig.canvas.mpl_connect('scroll_event', onScrollEvent)
svelocity.on_changed(onDialChange)

interval = 100 * dt

ani = animation.FuncAnimation(
    fig, animate, interval=interval, init_func=init)

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
# ani.save('x.mp4', fps=30, dpi=500, extra_args=['-vcodec', 'libx264'])

plt.show()
