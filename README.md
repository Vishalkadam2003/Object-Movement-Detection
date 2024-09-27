Motion Detection App
This is a Python-based Motion Detection App using OpenCV, Tkinter, and Pygame. It captures motion using a webcam, alerts users via sound, optionally saves images or videos of detected movements, and sends email notifications with the captured images. The app also features a dark mode interface and customizable settings, making it user-friendly and functional for various use cases.

Features
Real-Time Motion Detection: Detects motion using the webcam with adjustable sensitivity.
Customizable Alert Sound: Choose from a default alert sound or upload your custom sound file.
Email Notifications: Sends email alerts with captured images when motion is detected.
Save Images/Videos: Optionally save images or video clips when motion is detected.
Dark Mode Interface: Visually appealing and easy-to-use interface with dark mode enabled.
Log Tracking: Keeps track of motion detection events and logs them with a timestamp.
Custom Background: Allows you to set a custom background image for the app.
Requirements
Make sure to have the following installed before running the app:

Python 3.x
OpenCV: pip install opencv-python
Tkinter: Pre-installed with Python, or install using pip install python-tk
Pygame: pip install pygame
Pillow: pip install Pillow
imutils: pip install imutils
smtplib: Pre-installed with Python (used for sending email alerts)

How It Works
The app starts motion detection using your webcam.
You can start/pause the detection using the Start Detection button.
Adjust sensitivity using the Sensitivity Scale to fine-tune the detection.
Check the Save Images/Videos option to automatically save images or video clips when motion is detected.
Enable Email Alerts to receive an email notification with the captured image attached.
The motion detection area is highlighted with a green rectangle on the live feed.
The app maintains a log of motion detection events with timestamps, displayed on the main interface.
The detection can be stopped at any time using the Stop Detection button.
Customization
Change Alert Sound: Use the Select Custom Sound button to choose your own alert sound file.
Modify Background: Change the path to a custom background image in the set_background() function.
Controls
Start/Pause Detection: Begin or pause motion detection.
Stop Detection: Fully stop the detection process.
Save Images/Videos: Toggle saving images/videos when motion is detected.
Email Alerts: Enable email notifications for detected motion.
Sensitivity Adjustment: Adjust detection sensitivity using the slider.
