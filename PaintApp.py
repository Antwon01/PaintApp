import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.canvas_width = 500
        self.canvas_height = 300
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            bd=3,
            relief=tk.SUNKEN
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.setup_navbar()
        self.setup_tools()
        self.setup_events()
        self.prev_x = None
        self.prev_y = None

        # Initialize undo stack
        self.undo_stack = []
        self.current_action = []

    def setup_navbar(self):
        self.navbar = tk.Menu(self.root)
        self.root.config(menu=self.navbar)

        # File Menu
        self.file_menu = tk.Menu(self.navbar, tearoff=False)
        self.navbar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save Snapshot", command=self.take_snapshot)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit Menu
        self.edit_menu = tk.Menu(self.navbar, tearoff=False)
        self.navbar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")

        # Bind keyboard shortcut for Undo
        self.root.bind_all("<Control-z>", lambda event: self.undo())

    def setup_tools(self):
        self.selected_tool = 'pen'
        self.colors = ['black', 'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'white']
        self.selected_color = self.colors[0]
        self.brush_sizes = [2, 4, 6, 8]
        self.selected_size = self.brush_sizes[0]
        self.pen_types = ['line', 'round', 'square', 'arrow', 'diamond']
        self.selected_pen_type = self.pen_types[0]

        self.tool_frame = ttk.LabelFrame(self.root, text='Tools')
        self.tool_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.Y)

        self.pen_button = ttk.Button(self.tool_frame, text='Pen', command=self.select_pen_tool)
        self.pen_button.pack(side=tk.TOP, padx=5, pady=5)

        self.eraser_button = ttk.Button(self.tool_frame, text='Eraser', command=self.select_eraser_tool)
        self.eraser_button.pack(side=tk.TOP, padx=5, pady=5)

        self.brush_size_label = ttk.Label(self.tool_frame, text="Brush Size:")
        self.brush_size_label.pack(side=tk.TOP, padx=5, pady=5)

        self.brush_size_combobox = ttk.Combobox(
            self.tool_frame,
            values=self.brush_sizes,
            state='readonly'
        )
        self.brush_size_combobox.current(0)
        self.brush_size_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.brush_size_combobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self.select_size(int(self.brush_size_combobox.get()))
        )

        self.color_label = ttk.Label(self.tool_frame, text='Color:')
        self.color_label.pack(side=tk.TOP, padx=5, pady=5)

        self.color_combobox = ttk.Combobox(
            self.tool_frame,
            values=self.colors,
            state='readonly'
        )
        self.color_combobox.current(0)
        self.color_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.color_combobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self.select_color(self.color_combobox.get())
        )

        self.pen_type_label = ttk.Label(self.tool_frame, text="Pen Type:")
        self.pen_type_label.pack(side=tk.TOP, padx=5, pady=5)

        self.pen_combobox = ttk.Combobox(
            self.tool_frame,
            values=self.pen_types,
            state='readonly'
        )
        self.pen_combobox.current(0)
        self.pen_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.pen_combobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self.select_pen_type(self.pen_combobox.get())
        )

        self.clear_button = ttk.Button(self.tool_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_button.pack(side=tk.TOP, padx=5, pady=5)

    def setup_events(self):
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

    def select_pen_tool(self):
        self.selected_tool = 'pen'

    def select_eraser_tool(self):
        self.selected_tool = 'eraser'
        self.selected_color = 'white'  # Typically, eraser sets color to background

    def select_size(self, size):
        self.selected_size = size

    def select_color(self, color):
        self.selected_color = color

    def select_pen_type(self, pen_type):
        self.selected_pen_type = pen_type

    def start_draw(self, event):
        self.prev_x = event.x
        self.prev_y = event.y
        self.current_action = []  # Start a new action

    def draw(self, event):
        if self.selected_tool == 'pen':
            if self.prev_x is not None and self.prev_y is not None:
                if self.selected_pen_type == 'line':
                    item = self.canvas.create_line(
                        self.prev_x, self.prev_y, event.x, event.y,
                        fill=self.selected_color,
                        width=self.selected_size,
                        smooth=True
                    )
                elif self.selected_pen_type == 'round':
                    x1 = event.x - self.selected_size
                    y1 = event.y - self.selected_size
                    x2 = event.x + self.selected_size
                    y2 = event.y + self.selected_size
                    item = self.canvas.create_oval(
                        x1, y1, x2, y2,
                        fill=self.selected_color,
                        outline=self.selected_color
                    )
                elif self.selected_pen_type == 'square':
                    x1 = event.x - self.selected_size
                    y1 = event.y - self.selected_size
                    x2 = event.x + self.selected_size
                    y2 = event.y + self.selected_size
                    item = self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=self.selected_color,
                        outline=self.selected_color
                    )
                elif self.selected_pen_type == 'arrow':
                    item = self.canvas.create_line(
                        self.prev_x, self.prev_y, event.x, event.y,
                        fill=self.selected_color,
                        width=self.selected_size,
                        arrow=tk.LAST
                    )
                elif self.selected_pen_type == 'diamond':
                    x_center = event.x
                    y_center = event.y
                    size = self.selected_size
                    points = [
                        x_center, y_center - size,  # Top
                        x_center + size, y_center,  # Right
                        x_center, y_center + size,  # Bottom
                        x_center - size, y_center   # Left
                    ]
                    item = self.canvas.create_polygon(
                        points,
                        fill=self.selected_color,
                        outline=self.selected_color
                    )
                else:
                    item = None

                if item:
                    self.current_action.append(item)

                self.prev_x = event.x
                self.prev_y = event.y

        elif self.selected_tool == 'eraser':
            item = self.canvas.create_line(
                self.prev_x, self.prev_y, event.x, event.y,
                fill='white',
                width=self.selected_size,
                capstyle=tk.ROUND,
                smooth=True
            )
            self.current_action.append(item)
            self.prev_x = event.x
            self.prev_y = event.y

    def end_draw(self, event):
        if self.current_action:
            self.undo_stack.append(self.current_action)
            self.current_action = []
        self.prev_x = None
        self.prev_y = None

    def clear_canvas(self):
        if messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas? This action cannot be undone."):
            self.canvas.delete("all")
            self.undo_stack.clear()

    def take_snapshot(self):
        try:
            self.canvas.postscript(file="snapshot.eps")
            messagebox.showinfo("Snapshot Saved", "Snapshot saved as snapshot.eps")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving snapshot: {e}")

    def undo(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        last_action = self.undo_stack.pop()
        for item_id in last_action:
            self.canvas.delete(item_id)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Paint Application")
    app = PaintApp(root)
    root.mainloop()
