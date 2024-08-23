import tkinter as tk
import math
import threading
import time
from datetime import datetime, timedelta
import configparser


class CountbackTimer:
    def __init__(self, master):
        self.master = master
        self.master.title("Countback Timer")
        self.canvas_height = 300
        self.canvas_width = 300
        
        # Canvas to draw the timer
        self.canvas = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_height, bd=0, highlightthickness=0)
        self.canvas.pack()
        # aa
        # Timer variables
        self.initial_timer_mins = 5  # Initial countdown time in seconds
        self.initial_timer_secs = 60 * self.initial_timer_mins  # Initial countdown time in seconds
        self.total_mins = 10
        self.total_secs = self.total_mins * 60 

        self.timer_secs = self.initial_timer_secs
        self.timer_id = None


        # LabelFrame for global time
        self.global_time_frame = tk.LabelFrame(self.master, text="")
        self.global_time_frame.pack()
        
        # Global time variables
        self.global_time_seconds = 0
        self.global_time_label = tk.Label(self.global_time_frame, text="00:00", font=("Comic Sans MS", 12))
        self.global_time_label.pack()


        # Flag to track if the timer is currently running
        self.timer_running = False

        # Draw the initial timer
        self.draw_timer()

        # Start/Stop button
        # Counter variables
        self.start_counter = 0
        self.start_stop_button = tk.Button(self.master, text=f"Start: {self.start_counter}", command=self.toggle_timer)
        self.start_stop_button.pack()

        # Reset button
        self.reset_button = tk.Button(self.master, text="Reset", command=self.reset_timer)
        self.reset_button.pack()

        # Start the global time update thread
        self.global_time_thread = threading.Thread(target=self.update_global_time)
        self.global_time_thread.daemon = True
        self.global_time_thread.start()


    def draw_timer(self):
        # Coordinates of the arc's bounding box
        self.x1, self.y1, self.x2, self.y2 = self.canvas_width*0.1, self.canvas_height*0.1, self.canvas_width*0.9, self.canvas_height*0.9 # x1: left x, x2: right x


        self.degree_per_sec = 360 / self.total_secs
        self.degree_per_min = 360 / self.total_mins
        self.mid_x = (self.x1 + self.x2) / 2
        self.mid_y = (self.y1 + self.y2) / 2

        self.draw_circle_and_arc(front_arc_color="orange", back_circle_color="dark blue")
        self.draw_circle_time_dials()
        #self.draw_bar()

    def draw_bar(self):
        # Total height of the rectangle
        self.total_height = 100

        # Draw labels (1~12) on the side of the rectangle
        for i in range(1, 13):
            label_x = 35
            label_y = self.y1 + i * (self.total_height / 12) - (self.total_height / 12) / 2  # Align to the bottom
            self.canvas.create_text(label_x, label_y, text=str(i), anchor=tk.W, font=("Helvetica", 8), fill="black")

        # Draw the vertical bar (rectangle) on the left of the circle
        bar_width = 10
        current_time = time.localtime()
        hours = current_time.tm_hour
        minutes = current_time.tm_min

        # Calculate the length of the rectangle based on the current time
        length = (hours % 3) * (self.total_height / 12) + (minutes / 60) * (self.total_height / 12)

        start_x = 20 - bar_width / 2
        start_y = self.y1
        end_x = 30 + bar_width / 2
        end_y = start_y + length

        self.canvas.create_rectangle(start_x, start_y, end_x, end_y, fill="green", outline="black")


    def draw_circle_and_arc(self, front_arc_color="red", back_circle_color="navy"):
        # Draw the navy-filled circle as background
        self.canvas.create_oval(self.x1, self.y1, self.x2, self.y2, outline="black", fill=back_circle_color)

        # Draw the red-filled arc
        start_angle = 90  # Start angle is 90 degrees
        extent = -self.timer_secs * self.degree_per_sec  # Each arc will cover 6 degrees per second

        self.canvas.create_arc(self.x1, self.y1, self.x2, self.y2, start=start_angle, extent=extent,
                               style=tk.PIESLICE, outline="black", fill=front_arc_color)

    def draw_circle_time_dials(self):
        # Draw time dials and numbers at the bottom
        for mins in range(0, self.initial_timer_mins + 1, 1):
            angle = math.radians(90 - mins * self.degree_per_min)  # Convert seconds to degrees
            self.radius = (self.x2-self.x1) / 2 *1.05


            x = self.mid_x + self.radius * math.cos(angle)
            y = self.mid_y - self.radius * math.sin(angle)

            # Draw time dial
            self.canvas.create_line(self.mid_x, self.mid_y, x, y, fill="black")

            # Draw number
            number_x = self.mid_x + (self.radius + 10) * math.cos(angle)  # Place the number slightly outside the arc
            number_y = self.mid_y - (self.radius + 10) * math.sin(angle)

            self.canvas.create_text(number_x, number_y, text=str(mins), font=("Comic Sans MS", 8), fill="black")

    def toggle_timer(self):
        if not self.timer_running:
            # Start the timer
            self.start_stop_button.config(text=f"Stop: {self.start_counter}")
            self.timer_running = True
            self.update_timer()
        else:
            # Stop the timer
            self.start_stop_button.config(text=f"Start: {self.start_counter}")
            self.timer_running = False
            self.master.after_cancel(self.timer_id)

    def update_timer(self):
        if self.timer_secs > 0 and self.timer_running:
            self.timer_secs -= 1
            if self.timer_secs == 0:
                self.start_counter += 1  # Increment the counter
            self.canvas.delete("all")  # Clear the canvas
            self.draw_timer()
            self.timer_id = self.master.after(1000, self.update_timer)
        elif self.timer_secs == 0:
            self.canvas.create_text(self.mid_x, self.mid_y, text="Time's up!", font=("Comic Sans MS", 12), fill="red")
            # Automatically reset to the initial timer value after 4 seconds
            self.master.after(4000, self.reset_timer)

    def reset_timer(self):
        # Reset the timer to its initial value
        self.timer_secs = self.initial_timer_secs
        self.canvas.delete("all")
        self.draw_timer()
        self.start_stop_button.config(text=f"Start: {self.start_counter}")
        self.timer_running = False
        self.master.after_cancel(self.timer_id)

    def update_global_time(self):
        #while True:
        current_time = time.localtime()
        time_str = time.strftime("%I:%M:%S %p", current_time)
        self.global_time_label.config(text= time_str)
            
        # Schedule the next update after 1000 milliseconds (1 second)
        self.master.after(1000, self.update_global_time)
        #time.sleep(1)

# Create the main window
root = tk.Tk()



# Create a CountbackTimer instance
countdown_timer = CountbackTimer(root)

# Run the Tkinter event loop
root.mainloop()