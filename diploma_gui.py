import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from diploma_generator import DiplomaGenerator
from pathlib import Path

class DiplomaGeneratorGUI:
    def __init__(self):
        self.generator = DiplomaGenerator()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Diploma Generator")
        self.root.geometry("600x400")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Template selection
        ttk.Label(self.main_frame, text="Template File:").grid(row=0, column=0, sticky=tk.W)
        self.template_path = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.template_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_template).grid(row=0, column=2)
        
        # Names file selection
        ttk.Label(self.main_frame, text="Names File:").grid(row=1, column=0, sticky=tk.W)
        self.names_path = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.names_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_names).grid(row=1, column=2)
        
        # Placeholder entry
        ttk.Label(self.main_frame, text="Name Placeholder:").grid(row=2, column=0, sticky=tk.W)
        self.placeholder = tk.StringVar(value="[NAME]")
        ttk.Entry(self.main_frame, textvariable=self.placeholder, width=50).grid(row=2, column=1, padx=5)
        
        # Output format selection
        ttk.Label(self.main_frame, text="Output Format:").grid(row=3, column=0, sticky=tk.W)
        self.output_format = tk.StringVar(value="pdf")
        format_frame = ttk.Frame(self.main_frame)
        format_frame.grid(row=3, column=1, sticky=tk.W)
        ttk.Radiobutton(format_frame, text="PDF", variable=self.output_format, value="pdf").grid(row=0, column=0)
        ttk.Radiobutton(format_frame, text="Word", variable=self.output_format, value="docx").grid(row=0, column=1)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.output_format, value="png").grid(row=0, column=2)
        
        # Output directory selection
        ttk.Label(self.main_frame, text="Output Directory:").grid(row=4, column=0, sticky=tk.W)
        self.output_dir = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.output_dir, width=50).grid(row=4, column=1, padx=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_output).grid(row=4, column=2)
        
        # Generate button
        ttk.Button(self.main_frame, text="Generate Diplomas", command=self.generate_diplomas).grid(row=5, column=1, pady=20)
        
        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(self.main_frame, textvariable=self.status_var).grid(row=6, column=0, columnspan=3)
        
        # Configure grid
        for i in range(7):
            self.main_frame.grid_rowconfigure(i, pad=10)
        
    def browse_template(self):
        filetypes = [
            ('All supported files', '*.pdf;*.docx;*.doc;*.jpg;*.jpeg;*.png'),
            ('PDF files', '*.pdf'),
            ('Word files', '*.docx;*.doc'),
            ('Image files', '*.jpg;*.jpeg;*.png')
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.template_path.set(filename)
            
    def browse_names(self):
        filetypes = [('Text files', '*.txt'), ('All files', '*.*')]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.names_path.set(filename)
            
    def browse_output(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
            
    def generate_diplomas(self):
        try:
            # Validate inputs
            if not self.template_path.get():
                raise ValueError("Please select a template file")
            if not self.names_path.get():
                raise ValueError("Please select a names file")
            if not self.output_dir.get():
                raise ValueError("Please select an output directory")
                
            # Load template
            self.status_var.set("Loading template...")
            self.root.update()
            self.generator.load_template(self.template_path.get())
            
            # Load names
            self.status_var.set("Loading names...")
            self.root.update()
            names = self.generator.load_names(self.names_path.get())
            
            # Generate diplomas
            self.status_var.set("Generating diplomas...")
            self.root.update()
            self.generator.generate_diplomas(
                names=names,
                output_dir=self.output_dir.get(),
                placeholder=self.placeholder.get(),
                output_format=self.output_format.get()
            )
            
            self.status_var.set("Diplomas generated successfully!")
            messagebox.showinfo("Success", "Diplomas have been generated successfully!")
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DiplomaGeneratorGUI()
    app.run() 