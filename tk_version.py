import tkinter as tk

class TransparentReminder(tk.Tk):
    def __init__(self, text):
        super().__init__()

        # Set window to be transparent and always on top
        self.attributes('-topmost', True)  # Keeps the window on top
        self.overrideredirect(True)  # Removes window border and title bar
        self.config(bg='black')  # Set the background color to black (transparent effect)

        # Set the window transparency (alpha)
        self.attributes('-alpha', 0.2)  # Adjust the transparency (0.0 to 1.0)

        # Create the label with the reminder text
        self.label = tk.Label(self, text=text, font=('Arial', 24), fg='white', bg='black')
        self.label.pack()

        # Center the label
        self.update_idletasks()  # Update the window size
        width = self.label.winfo_width()
        height = self.label.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')  # Set window size and position

        # Make the window click-through by capturing all mouse events
        self.bind("<Button-1>", self.ignore_click)
        self.bind("<Button-3>", self.quit_app)  # Right-click to quit the app

    def ignore_click(self, event):
        # Ignores mouse clicks, allowing interaction with underlying windows
        pass

    def quit_app(self, event):
        # Exits the application on right-click
        self.quit()

def main():
    reminder_text = "Stay focused on the task at hand!"
    app = TransparentReminder(reminder_text)
    app.mainloop()

if __name__ == "__main__":
    main()
