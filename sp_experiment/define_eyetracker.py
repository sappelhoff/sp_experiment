"""Functions and settings for the tobii 4C eye tracker.

Tobii Research "Pro" license is required (to be purchased separately).
"""
import os
import platform
import glob
import subprocess

import tobii_research as tr


def call_eyetracker_manager_calibration(address):
    """Start the Tobii Eye Tracking Manager for calibration."""
    try:
        os_type = platform.system()
        ETM_PATH = ''
        DEVICE_ADDRESS = address
        if os_type == 'Windows':
            ETM_PATH = glob.glob(os.environ['LocalAppData'] +
                                 '/TobiiProEyeTrackerManager/app-*/TobiiProEyeTrackerManager.exe')[0]  # noqa: E501
        elif os_type == 'Linux':
            ETM_PATH = 'TobiiProEyeTrackerManager'
        elif os_type == 'Darwin':
            ETM_PATH = '/Applications/TobiiProEyeTrackerManager.app/Contents/MacOS/TobiiProEyeTrackerManager'  # noqa:E501
        else:
            raise OSError('Unsupported platform: {}'.format(os_type))

        eyetracker = tr.EyeTracker(DEVICE_ADDRESS)

        mode = 'usercalibration'

        etm_p = subprocess.Popen([ETM_PATH,
                                  '--mode=' + mode,
                                  '--device-address=' + eyetracker.address],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=False)

        stdout, stderr = etm_p.communicate()

        if etm_p.returncode == 0:
            print('Eye Tracker Manager was called successfully!')
        else:
            print('Eye Tracker Manager call returned the error code: {}'.format(etm_p.returncode))  # noqa: E501
            errlog = None
            if os_type == 'Windows':
                # On Windows ETM error messages are logged to stdout
                errlog = stdout
            else:
                errlog = stderr

            for line in errlog.splitlines():
                if line.startswith('ETM Error:'):
                    print(line)

    except Exception as e:
        print(e)
