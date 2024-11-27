import os
import tkinter as tk
from tkinter import filedialog, messagebox

class FileMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess File Mover - Folder Explorer")
        
        # Add keyboard binding
        self.root.bind('<Key>', self.handle_keypress)
        
        # Colors
        self.light_square = "#FFFFFF"  # White
        self.dark_square = "#86A666"   # Green
        self.highlight_color = "#fff7aa"  # Yellow for possible moves
        self.selected_color = "#ff9999"  # Red for king
        self.enemy_color = "#000000"    # Black for enemy pieces
        
        # State variables
        self.directory = None
        self.current_path = None  # Track current directory path
        self.file_list = []
        self.folder_list = []
        self.king_file = None
        self.king_position = None
        self.possible_moves = []
        self.score = 0
        self.level = 1  # Track current level
        
        # Add a back button for navigation
        self.create_widgets()

    def create_widgets(self):
        # Top frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        # Directory selection button
        tk.Button(control_frame, text="Select Directory", command=self.select_directory).pack(side=tk.LEFT, padx=5)
        
        # King selection button
        tk.Button(control_frame, text="Select King", command=self.select_king).pack(side=tk.LEFT, padx=5)
        
        # Back button (initially disabled)
        self.back_button = tk.Button(control_frame, text="⬅ Back", command=self.go_back, state='disabled')
        self.back_button.pack(side=tk.LEFT, padx=5)
        
        # Level and path display
        self.path_label = tk.Label(control_frame, text="Level 1: Root", font=('Arial', 10))
        self.path_label.pack(side=tk.LEFT, padx=20)
        
        # Score display
        self.score_label = tk.Label(control_frame, text="Captures: 0", font=('Arial', 12))
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        # Chess board frame
        board_frame = tk.Frame(self.root)
        board_frame.pack(padx=20, pady=20)
        
        # Create chess board
        self.board_squares = []
        for row in range(8):
            square_row = []
            for col in range(8):
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                square = tk.Frame(board_frame, width=60, height=60, bg=color)
                square.grid(row=row, column=col, padx=1, pady=1)
                square.grid_propagate(False)
                square.bind('<Button-1>', lambda e, r=row, c=col: self.square_clicked(r, c))
                square_row.append(square)
            self.board_squares.append(square_row)

    def select_directory(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.current_path = self.directory  # Set initial path
            self.load_current_directory()
            self.path_label.config(text=f"Level {self.level}: {os.path.basename(self.current_path) or 'Root'}")
            messagebox.showinfo("Directory Selected", "Now select your King piece!")

    def load_current_directory(self):
        """Load files and folders from the current directory"""
        self.file_list = [f for f in os.listdir(self.current_path) 
                          if os.path.isfile(os.path.join(self.current_path, f))]
        self.folder_list = [f for f in os.listdir(self.current_path) 
                           if os.path.isdir(os.path.join(self.current_path, f))]
        self.display_pieces()

    def select_king(self):
        if not self.directory:
            messagebox.showwarning("No Directory", "Please select a directory first!")
            return
            
        if not self.file_list:
            messagebox.showwarning("No Files", "No files available to select as King!")
            return
            
        # Create selection window
        select_window = tk.Toplevel(self.root)
        select_window.title("Select Your King")
        
        # Create listbox with files
        listbox = tk.Listbox(select_window, width=50)
        listbox.pack(padx=10, pady=10)
        
        for file in self.file_list:
            listbox.insert(tk.END, file)
            
        def confirm_selection():
            selection = listbox.curselection()
            if selection:
                self.king_file = self.file_list[selection[0]]
                # Store the full path of the king file
                self.king_file_path = os.path.join(self.current_path, self.king_file)
                self.king_position = (7, 4)  # Start at bottom center
                self.display_pieces()
                select_window.destroy()
        
        tk.Button(select_window, text="Confirm Selection", command=confirm_selection).pack(pady=10)

    def display_pieces(self):
        # Clear the board
        for row in self.board_squares:
            for square in row:
                for widget in square.winfo_children():
                    widget.destroy()
        
        # Display king if selected
        if self.king_file and self.king_position:
            row, col = self.king_position
            king_frame = tk.Frame(
                self.board_squares[row][col],
                bg=self.selected_color,
                width=58,
                height=58
            )
            king_frame.place(relx=0.5, rely=0.5, anchor='center')
            
            label = tk.Label(
                king_frame,
                text=f"{self.king_file[:10]}...\n👑",
                wraplength=55,
                font=('Arial', 8),
                bg=self.selected_color
            )
            label.pack(expand=True)
            
            # Bind click event to both frame and label
            king_frame.bind('<Button-1>', lambda e: self.square_clicked(row, col))
            label.bind('<Button-1>', lambda e: self.square_clicked(row, col))
        
        # Display folders as enemy pieces
        for i, folder in enumerate(self.folder_list):
            if i >= 8:  # Limit to top row
                break
            label = tk.Label(
                self.board_squares[0][i],
                text=f"{folder[:10]}...\n♟",
                wraplength=55,
                font=('Arial', 8),
                fg='white',
                bg=self.enemy_color
            )
            label.place(relx=0.5, rely=0.5, anchor='center')

    def square_clicked(self, row, col):
        print(f"Clicked square at ({row}, {col})")
        print(f"King position is {self.king_position}")

        # If clicking the king's position
        if self.king_position == (row, col):
            print("Clicked king's position")
            self.highlight_king_moves(row, col)
            return

        # If a move is possible to this square
        if (row, col) in self.possible_moves:
            print("Moving to valid position")
            self.move_king(row, col)
            return

        # Clear highlights if clicking elsewhere
        print("Clearing highlights")
        self.clear_highlights()
        self.display_pieces()

    def highlight_king_moves(self, row, col):
        self.clear_highlights()
        
        possible_moves = [
            (row-1, col),   # Up
            (row+1, col),   # Down
            (row, col-1),   # Left
            (row, col+1),   # Right
        ]
        
        self.possible_moves = [
            (r, c) for r, c in possible_moves 
            if 0 <= r < 8 and 0 <= c < 8
        ]
        
        for r, c in self.possible_moves:
            highlight = tk.Frame(
                self.board_squares[r][c],
                bg=self.highlight_color,
                width=58,
                height=58
            )
            highlight.place(relx=0.5, rely=0.5, anchor='center')
            highlight.bind('<Button-1>', lambda e, new_r=r, new_c=c: self.move_king(new_r, new_c))
            
            for widget in self.board_squares[r][c].winfo_children():
                if isinstance(widget, tk.Label):
                    widget.lift()

    def clear_highlights(self):
        for row in self.board_squares:
            for square in row:
                for widget in square.winfo_children():
                    if isinstance(widget, tk.Frame) and widget.cget('bg') == self.highlight_color:
                        widget.destroy()

    def move_king(self, new_row, new_col):
        print(f"Moving king to ({new_row}, {new_col})")
        print(f"Current king file path: {self.king_file_path}")  # Debug print
        
        # Check if there's a folder at the new position
        for widget in self.board_squares[new_row][new_col].winfo_children():
            if isinstance(widget, tk.Label) and "♟" in widget.cget('text'):
                folder_text = widget.cget('text').split('\n')[0].replace('...', '')
                folder_name = next((f for f in self.folder_list if f.startswith(folder_text)), None)
                if folder_name:
                    try:
                        # Get full paths
                        folder_path = os.path.join(self.current_path, folder_name)
                        new_file_path = os.path.join(folder_path, self.king_file)
                        
                        print(f"Moving from {self.king_file_path} to {new_file_path}")  # Debug print
                        
                        # Move the file
                        os.rename(self.king_file_path, new_file_path)
                        self.king_file_path = new_file_path  # Update the king's path
                        print(f"Moved {self.king_file} to {folder_path}")
                        
                        # Enter the folder
                        self.enter_folder(folder_name)
                        return
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to move file: {str(e)}\nFrom: {self.king_file_path}\nTo: {new_file_path}")
                        return
        
        # If no folder at destination, just move the king
        self.king_position = (new_row, new_col)
        self.clear_highlights()
        self.possible_moves = []
        self.display_pieces()

    def enter_folder(self, folder_name):
        """Enter a new folder and set up the next level"""
        self.current_path = os.path.join(self.current_path, folder_name)
        self.level += 1
        self.back_button.config(state='normal')
        self.path_label.config(text=f"Level {self.level}: {folder_name}")
        
        # Reset king position to bottom center
        self.king_position = (7, 4)
        
        # Load new directory contents
        self.load_current_directory()
        messagebox.showinfo("Folder Entered", f"Moved '{self.king_file}' into folder: {folder_name}")

    def go_back(self):
        """Go back to the previous directory and move the file back if desired"""
        if self.current_path != self.directory:
            # Ask if user wants to move the file back
            if messagebox.askyesno("Move File", "Do you want to move the file back to the parent directory?"):
                try:
                    # Get paths
                    parent_path = os.path.dirname(self.current_path)
                    new_file_path = os.path.join(parent_path, self.king_file)
                    
                    # Move file back
                    os.rename(self.king_file_path, new_file_path)
                    self.king_file_path = new_file_path  # Update the king's path
                    print(f"Moved {self.king_file} back to {parent_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to move file back: {str(e)}")
                    return
            
            # Update current path
            self.current_path = os.path.dirname(self.current_path)
            self.level -= 1
            self.path_label.config(text=f"Level {self.level}: {os.path.basename(self.current_path) or 'Root'}")
            
            # Disable back button if we're at root
            if self.current_path == self.directory:
                self.back_button.config(state='disabled')
            
            # Reset king position
            self.king_position = (7, 4)
            
            # Load directory contents
            self.load_current_directory()

    def handle_keypress(self, event):
        if not self.king_position:  # If no king is selected, ignore keyboard
            return
        
        row, col = self.king_position
        new_row, new_col = row, col
        
        # Handle arrow keys and WASD
        if event.keysym in ['Up', 'w', 'W']:
            new_row -= 1
        elif event.keysym in ['Down', 's', 'S']:
            new_row += 1
        elif event.keysym in ['Left', 'a', 'A']:
            new_col -= 1
        elif event.keysym in ['Right', 'd', 'D']:
            new_col += 1
        
        # Check if the move is valid
        if (0 <= new_row < 8 and 0 <= new_col < 8 and 
            (new_row, new_col) != self.king_position):
            print(f"Keyboard move to ({new_row}, {new_col})")
            
            # Show possible moves first
            self.highlight_king_moves(row, col)
            
            # If the move is in possible moves, execute it
            if (new_row, new_col) in self.possible_moves:
                self.move_king(new_row, new_col)
            else:
                self.clear_highlights()
                self.display_pieces()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMoverApp(root)
    root.mainloop()     