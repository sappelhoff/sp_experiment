"""Define monitors."""
from psychopy import monitors

# All available monitors
print(monitors.getAllMonitors())

# Define new monitors
# My Lenovo P51 monitor
my_monitor = monitors.Monitor(name='p51')
my_monitor.setSizePix((1920, 1080))
my_monitor.setWidth(34.6)  # width of display in cm
my_monitor.setDistance(50)  # distance of eyes from screen in cm
my_monitor.saveMon()
