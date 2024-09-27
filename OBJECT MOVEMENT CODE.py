import cv2
import time
import imutils
import pygame
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk
from tkinter import filedialog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Initialize Pygame mixer outside the class
pygame.mixer.init()

class MotionDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motion Detection App")
        self.set_background()

        # Dark Mode Colors
        self.bg_color = "#1E1E1E"
        self.text_color = "white"
        self.button_color = "#303030"
        self.button_hover_color = "#404040"
        self.canvas_color = "#2E2E2E"

        # Initialize variables
        self.alert_sound = pygame.mixer.Sound("C:/Users/HP/OneDrive/One drive/Documents/PROJECT - AIwoof/beep-01a.wav")
        self.custom_sound = None  # For custom alert sound
        self.img_filename = None
        self.save_var = tk.BooleanVar()
        self.email_var = tk.BooleanVar()

        self.cam = cv2.VideoCapture(0)
        time.sleep(1)

        self.background_model = None
        self.area = 10000  # Increased the area threshold to detect larger movements
        self.motion_history = []
        self.history_limit = 5  # Number of frames to keep track of motion
        self.is_detection_running = False
        self.is_paused = False  # Flag to control the pause state
        self.detection_count = 0  # Counter for detected movements

        self.video_thread = Thread(target=self.detect_motion)
        self.video_thread.daemon = True

        # Adjustable Sensitivity
        self.sensitivity_scale = tk.Scale(self.root, label="Sensitivity", from_=1, to=100, orient=tk.HORIZONTAL,
                                          bg=self.bg_color, fg=self.text_color)
        self.sensitivity_scale.set(50)
        self.sensitivity_scale.pack()

        # Create a frame for buttons in the middle
        self.left_frame = tk.Frame(self.root, bg=self.bg_color)
        self.left_frame.pack(expand=True)

        self.create_widgets()

    def set_background(self):
        background_image_path = "C:/Users/HP/OneDrive/One drive/Documents/PROJECT - AIwoof/wallpaperflare.com_wallpaper (3).jpg"  # Change this to the path of your background image
        background_image = Image.open(background_image_path)
        background_image = background_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.BICUBIC)
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.lower()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=1000, height=550, bg=self.canvas_color)
        self.canvas.pack()

        # Define button colors
        button_colors = {
            'start_pause': '#4CAF50',  # Green
            'stop': '#F44336',        # Red
            'save': '#2196F3',        # Blue
            'email': '#9C27B0',       # Purple
            'custom_sound': '#FF5722' # Orange
        }

        button_hover_colors = {
            'start_pause': '#45A049',
            'stop': '#E53935',
            'save': '#1976D2',
            'email': '#7B1FA2',
            'custom_sound': '#E64A19'
        }

        # Create colorful buttons with gradients
        self.start_pause_button = tk.Button(self.left_frame, text="Start Detection", command=self.toggle_detection,
                                            font=('Helvetica', 14, 'bold'), fg='white', bg=button_colors['start_pause'], 
                                            activebackground=button_hover_colors['start_pause'], relief="flat", borderwidth=0,
                                            padx=20, pady=10)

        self.stop_button = tk.Button(self.left_frame, text="Stop Detection", command=self.stop_detection,
                                     font=('Helvetica', 14, 'bold'), fg='white', bg=button_colors['stop'], 
                                     activebackground=button_hover_colors['stop'], relief="flat", borderwidth=0,
                                     padx=20, pady=10)

        self.save_checkbox = tk.Checkbutton(self.root, text="Save Images/videos", variable=self.save_var,
                                            bg=self.bg_color, fg=button_colors['save'], selectcolor=self.bg_color,
                                            font=('Helvetica', 8), activebackground=button_hover_colors['save'])

        self.email_checkbox = tk.Checkbutton(self.root, text="Email Alerts", variable=self.email_var,
                                             bg=self.bg_color, fg=button_colors['email'], selectcolor=self.bg_color,
                                             font=('Helvetica', 10), activebackground=button_hover_colors['email'])

        self.custom_sound_button = tk.Button(self.root, text="Select Custom Sound", command=self.custom_sound,
                                             font=('Helvetica', 12, 'bold'), fg='white', bg=button_colors['custom_sound'],
                                             activebackground=button_hover_colors['custom_sound'], relief="flat", borderwidth=0,
                                             padx=20, pady=10)

        # Add tooltips for buttons
        self.create_tooltip(self.start_pause_button, "Start or Pause the motion detection")
        self.create_tooltip(self.stop_button, "Stop the motion detection")
        self.create_tooltip(self.save_checkbox, "Enable saving images or videos of detected motion")
        self.create_tooltip(self.email_checkbox, "Enable email alerts for detected motion")
        self.create_tooltip(self.custom_sound_button, "Select a custom sound for alerts")

        # Pack buttons
        self.start_pause_button.pack(side=tk.LEFT, padx=10)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        self.save_checkbox.pack(pady=10)
        self.email_checkbox.pack(pady=10)
        self.custom_sound_button.pack(pady=10)

        self.notification_label = tk.Label(self.root, text="", font=('Helvetica', 14), fg='green', bg=self.bg_color)
        self.notification_label.pack(pady=10)

        self.log_text = tk.Text(self.root, height=5, width=50, bg=self.bg_color, fg=self.text_color)
        self.log_text.pack()

    def create_tooltip(self, widget, text):
        tooltip = tk.Label(widget, text=text, background="lightyellow", relief="solid", borderwidth=1)
    
        def show_tooltip(event):
            tooltip.place(x=event.x_root, y=event.y_root)
    
        def hide_tooltip(event):
            tooltip.place_forget()
    
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def toggle_detection(self):
        if not self.is_detection_running:
            self.is_detection_running = True
            self.video_thread.start()
            self.start_pause_button.config(text="Pause Detection")
            self.notification_label.config(text="Detection Started")
        elif not self.is_paused:
            self.is_paused = True
            self.start_pause_button.config(text="Resume Detection")
            self.notification_label.config(text="Detection Paused")
        else:
            self.is_paused = False
            self.notification_label.config(text="Detection Resumed")

    def stop_detection(self):
        self.is_detection_running = False
        self.is_paused = False
        self.start_pause_button.config(text="Start Detection")
        self.notification_label.config(text="Detection Stopped")

    def send_email_alert(self, image_path):
        sender_email = "vishalkadam15082003@gmail.com"  # Enter your email address
        receiver_email = "a76684853@gmail.com"  # Enter the recipient's email address
        password = "Vishal1508@"  # Enter your email password

        subject = "Motion Detected!"
        body = "Motion has been detected. Check the attached image."

        msg = MIMEMultipart()
        msg.attach(MIMEText(body, 'plain'))

        # Attach the image
        with open(image_path, 'rb') as fp:
            img_data = MIMEImage(fp.read())
        msg.attach(img_data)

        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
            self.notification_label.config(text="Email alert sent")
        except Exception as e:
            print(f"Error sending email: {e}")
            self.notification_label.config(text="Error sending email alert")

    def detect_motion(self):
        while self.is_detection_running:
            if not self.is_paused:  # Check if the detection is not paused
                _, img = self.cam.read()
                text = "Normal"
                img = imutils.resize(img, width=1000)
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray_img = cv2.GaussianBlur(gray_img, (21, 21), 0)

                if self.background_model is None:
                    self.background_model = gray_img
                    continue

                sensitivity = self.sensitivity_scale.get()
                img_diff = cv2.absdiff(self.background_model, gray_img)
                thresh_img = cv2.threshold(img_diff, sensitivity, 255, cv2.THRESH_BINARY)[1]
                thresh_img = cv2.dilate(thresh_img, None, iterations=2)
                cnts = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # Check for significant movement
                detected_motion = False
                for c in cnts:
                    if cv2.contourArea(c) > self.area:
                        detected_motion = True
                        (x, y, w, h) = cv2.boundingRect(c)
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        text = "Moving Object Detected"

                        if self.custom_sound:
                            self.custom_sound.play()
                        else:
                                self.alert_sound.play()

                        # Log the event
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        log_message = f"{timestamp}: Motion detected at ({x}, {y})\n"
                        self.log_text.insert(tk.END, log_message)

                        # Save Images/Video Clips
                        if self.save_var.get():
                            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
                            self.img_filename = f"motion_{timestamp_str}.png"
                            cv2.imwrite(self.img_filename, img)

                if not detected_motion:
                    text = "Normal"
                    self.background_model = gray_img  # Update the background model
    
                cv2.putText(img, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.imgtk = imgtk
                self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
                self.root.update()

                # Email/Notification Alerts
                if self.email_var.get() and self.save_var.get():
                    self.send_email_alert(self.img_filename)
                else:
                # Reset detection count if no motion is detected
                    self.detection_count = 0

            time.sleep(0.1)  # Small delay to prevent high CPU usage

    # Release the camera when the detection loop is stopped
        self.cam.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = MotionDetectionApp(root)

    # Bind the 'q' key to stop the detection
    root.bind('<q>', lambda event: app.stop_detection())

    # Configure the root window for dark mode
    root.configure(bg=app.bg_color)

    root.mainloop()


