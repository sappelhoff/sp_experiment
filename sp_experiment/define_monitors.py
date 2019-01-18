"""Define monitors to be used.

main file: sp.py

This is important for psychopy to work in units of visual degrees.
"""
from psychopy import monitors

if __name__ == '__main__':
    # Define new monitors
    # -------------------

    # My Lenovo P51 monitor
    my_monitor = monitors.Monitor(name='p51')
    my_monitor.setSizePix((3840, 2160))
    my_monitor.setWidth(34.6)  # width of display in cm
    my_monitor.setDistance(50)  # distance of eyes from screen in cm
    my_monitor.saveMon()

    # My Dell Latitude 7490 monitor
    my_monitor = monitors.Monitor(name='latitude7490')
    my_monitor.setSizePix((1920, 1080))
    my_monitor.setWidth(30)
    my_monitor.setDistance(50)  # distance of eyes from screen in cm
    my_monitor.saveMon()

    # Eizo Foris monitor in the lab
    my_monitor = monitors.Monitor(name='eizoforis')
    my_monitor.setSizePix((2560, 1440))
    my_monitor.setWidth(60)
    my_monitor.setDistance(50)  # distance of eyes from screen in cm
    my_monitor.saveMon()

    # Add new monitor below

    # Print all available monitors
    print(monitors.getAllMonitors())
