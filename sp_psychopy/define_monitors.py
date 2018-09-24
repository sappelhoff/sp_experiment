"""Define monitors to be used.

This is important for psychopy to work in units of visual degrees.
"""
from psychopy import monitors

# Define new monitors
# -------------------

# My Lenovo P51 monitor
my_monitor = monitors.Monitor(name='p51')
my_monitor.setSizePix((1920, 1080))
my_monitor.setWidth(34.6)  # width of display in cm
my_monitor.setDistance(50)  # distance of eyes from screen in cm
my_monitor.saveMon()

# Print all available monitors
print(monitors.getAllMonitors())
