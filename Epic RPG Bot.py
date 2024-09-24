import tkinter as tk
from tkinter import ttk
import time
import threading
import pyautogui  # Simulates typing and pressing 'enter'

# Create a global lock for sending commands and a shared last_command_time
command_lock = threading.Lock()
last_command_time = 0  # Global variable to track the last time a command was sent
minimum_delay = 3  # Minimum delay between commands in seconds

# Create the main bot class
class EpicRPGBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Epic RPG AFK Bot")

        # Create a dictionary to store the intervals for each section
        self.intervals = {}
        self.threads = []
        self.running = False

        # Define the grid layout: 4 rows, 3 columns
        self.setup_gui()

    def setup_gui(self):
        # Row 1: Hunt, Adventure, Working
        self.create_dropdown_section(0, 0, "Hunt", ["rpg hunt", "rpg hunt h", "rpg hunt alone", "rpg hunt together", "rpg hunt h together"])
        self.create_dropdown_section(0, 1, "Adventure", ["rpg adventure", "rpg adventure h"])
        self.create_dropdown_section(0, 2, "Working", ["rpg chop", "rpg axe", "rpg bowsaw", "rpg chainsaw", "rpg fish", "rpg net", "rpg boat", "rpg bigboat", "rpg pickup", "rpg ladder", "rpg tractor", "rpg greenhouse", "rpg mine", "rpg pickaxe", "rpg drill", "rpg dynamite"])

        # Row 2: Farm, Lootbox
        self.create_dropdown_section(1, 0, "Farm", ["rpg farm", "rpg farm bread", "rpg farm carrot", "rpg farm potato"])
        self.create_dropdown_section(1, 1, "Lootbox", ["rpg buy common lootbox", "rpg buy uncommon lootbox", "rpg buy rare lootbox", "rpg buy epic lootbox", "rpg buy edgy lootbox"])

        # Row 3: Custom Command Section
        self.create_custom_command_section(2, 0)

        # Row 4: Convert to Seconds Section
        self.create_convert_seconds_section(3, 0)

        # Control Buttons
        self.start_button = tk.Button(self.root, text="Start", command=self.start_bot)
        self.start_button.grid(row=4, column=0)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_bot)
        self.stop_button.grid(row=4, column=1)

        self.close_button = tk.Button(self.root, text="Close", command=self.close_bot)
        self.close_button.grid(row=4, column=2)

    def create_dropdown_section(self, row, col, label, options):
        frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        frame.grid(row=row, column=col, padx=10, pady=10)

        label = tk.Label(frame, text=label)
        label.pack()

        # Dropdown for commands
        selected_command = tk.StringVar()
        dropdown = ttk.Combobox(frame, textvariable=selected_command, values=options)
        dropdown.pack()

        # Entry for interval (in seconds)
        interval_label = tk.Label(frame, text="Interval (seconds):")
        interval_label.pack()
        interval_entry = tk.Entry(frame)
        interval_entry.pack()

        self.intervals[label] = (dropdown, interval_entry)

    def create_custom_command_section(self, row, col):
        self.custom_frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        self.custom_frame.grid(row=row, column=col, columnspan=3, padx=10, pady=10)

        label = tk.Label(self.custom_frame, text="Custom Command")
        label.pack()

        self.custom_commands = []
        for i in range(3):  # Initially add three lines
            self.add_custom_command()

        # Button to add more custom lines
        add_button = tk.Button(self.custom_frame, text="Add More", command=self.add_custom_command)
        add_button.pack()

    def add_custom_command(self):
        # Create a frame for each custom command and place it vertically
        command_frame = tk.Frame(self.custom_frame)
        command_frame.pack(fill=tk.X)

        # Custom command entry
        custom_command = tk.Entry(command_frame)
        custom_command.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Custom interval entry
        custom_interval = tk.Entry(command_frame, width=10)
        custom_interval.pack(side=tk.LEFT, padx=5)

        self.custom_commands.append((custom_command, custom_interval))

    def create_convert_seconds_section(self, row, col):
        frame = tk.Frame(self.root, relief=tk.RAISED, borderwidth=2)
        frame.grid(row=row, column=col, columnspan=3, padx=10, pady=10)

        label = tk.Label(frame, text="Convert Minutes/Hours to Seconds")
        label.pack()

        # Entries for minutes and hours
        self.minutes_entry = tk.Entry(frame)
        self.minutes_entry.pack(side=tk.LEFT)
        self.hours_entry = tk.Entry(frame)
        self.hours_entry.pack(side=tk.LEFT)

        convert_button = tk.Button(frame, text="Convert", command=self.convert_to_seconds)
        convert_button.pack()

        self.convert_result = tk.Label(frame, text="")
        self.convert_result.pack()

    def convert_to_seconds(self):
        minutes = self.minutes_entry.get()
        hours = self.hours_entry.get()

        total_seconds = 0
        if minutes.isdigit():
            total_seconds += int(minutes) * 60
        if hours.isdigit():
            total_seconds += int(hours) * 3600

        self.convert_result.config(text=f"{total_seconds} seconds")

    def start_bot(self):
        if not self.running:  # Prevents starting the bot multiple times
            self.running = True
            time.sleep(1)  # Initial delay before starting (reduce from 15 seconds for testing)

            # Start separate threads for each section
            for section, (command_dropdown, interval_entry) in self.intervals.items():
                command = command_dropdown.get()
                interval = interval_entry.get()
                if command and interval.isdigit():
                    interval_seconds = int(interval)
                    thread = threading.Thread(target=self.send_command_loop, args=(command, interval_seconds))
                    self.threads.append(thread)
                    thread.start()

            # Start threads for custom commands
            for command_entry, interval_entry in self.custom_commands:
                command = command_entry.get()
                interval = interval_entry.get()
                if command and interval.isdigit():
                    interval_seconds = int(interval)
                    thread = threading.Thread(target=self.send_command_loop, args=(command, interval_seconds))
                    self.threads.append(thread)
                    thread.start()

    def send_command_loop(self, command, interval):
        global last_command_time

        while self.running:
            # Acquire the global lock to ensure only one command is sent at a time
            with command_lock:
                current_time = time.time()
                time_since_last_command = current_time - last_command_time

                # Ensure at least 3 seconds have passed since the last command
                if time_since_last_command < minimum_delay:
                    time.sleep(minimum_delay - time_since_last_command)

                # Simulate typing the command and pressing enter
                pyautogui.write(command)
                pyautogui.press('enter')
                print(f"Sent command: {command}")

                # Update last_command_time
                last_command_time = time.time()

            # Wait for the specified interval before sending the next command
            time.sleep(interval)

    def stop_bot(self):
        # Stops the bot without closing the application
        self.running = False
        # Join threads safely to stop them
        for thread in self.threads:
            thread.join()  # Wait for all threads to finish

        self.threads = []  # Clear thread list when stopped

    def close_bot(self):
        # Closes the application and stops all threads
        self.running = False
        for thread in self.threads:
            thread.join()  # Ensure all threads are safely stopped
        self.root.quit()

# Main function to run the bot
if __name__ == "__main__":
    root = tk.Tk()
    bot = EpicRPGBot(root)
    root.mainloop()
