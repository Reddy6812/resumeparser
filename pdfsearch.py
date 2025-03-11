import os
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def search_pdfs_in_folder(folder_path, search_terms):
    """Search for multiple terms (skills) in all PDF files within a folder and rank them."""
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    resume_scores = []

    for pdf in pdf_files:
        pdf_path = os.path.join(folder_path, pdf)
        try:
            doc = fitz.open(pdf_path)
            matched_terms = set()

            for page in doc:
                text = page.get_text("text").lower()
                for term in search_terms:
                    if term in text:
                        matched_terms.add(term)

            if matched_terms:
                resume_scores.append((pdf, len(matched_terms), list(matched_terms)))

        except Exception as e:
            print(f"Error reading {pdf}: {e}")

    # Sort resumes by the number of matched skills (Descending Order)
    resume_scores.sort(key=lambda x: x[1], reverse=True)
    return resume_scores

def browse_folder():
    """Open folder selection dialog."""
    folder_selected = filedialog.askdirectory()
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_selected)

def start_search():
    """Trigger the search process and display results."""
    folder_path = folder_path_entry.get()
    search_terms = search_term_entry.get().strip().lower().split(",")

    # Clean terms: remove spaces and empty entries
    search_terms = [term.strip() for term in search_terms if term.strip()]

    if not folder_path or not search_terms:
        messagebox.showerror("Input Error", "Please select a folder and enter at least one skill.")
        return

    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Invalid folder path. Please select a valid directory.")
        return

    results_text.config(state=tk.NORMAL)
    results_text.delete("1.0", tk.END)  # Clear previous results
    results_text.insert(tk.END, "Searching...\n")
    results_text.update_idletasks()

    matching_resumes = search_pdfs_in_folder(folder_path, search_terms)

    results_text.delete("1.0", tk.END)  # Clear progress text

    if matching_resumes:
        results_text.insert(tk.END, "Ranked Resumes (by Skills Matched):\n\n")
        for file, score, matched_skills in matching_resumes:
            results_text.insert(tk.END, f"{file} → {score} Skills Matched: {', '.join(matched_skills)}\n")
    else:
        results_text.insert(tk.END, "No resumes matched the given skills.")

    results_text.config(state=tk.DISABLED)

def copy_results():
    """Copy search results to clipboard."""
    text = results_text.get("1.0", tk.END)
    if text.strip():
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        messagebox.showinfo("Copied", "Results copied to clipboard!")

# Create GUI window
root = tk.Tk()
root.title("Resume Screening Tool")
root.geometry("700x500")

# Folder selection
tk.Label(root, text="Select Folder (Containing Resumes):").pack(anchor="w", padx=10, pady=5)
folder_frame = tk.Frame(root)
folder_frame.pack(fill="x", padx=10)

folder_path_entry = tk.Entry(folder_frame, width=50)
folder_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
tk.Button(folder_frame, text="Browse", command=browse_folder).pack(side="right")

# Skills input
tk.Label(root, text="Enter Required Skills (comma-separated):").pack(anchor="w", padx=10, pady=5)
search_term_entry = tk.Entry(root, width=50)
search_term_entry.pack(fill="x", padx=10, pady=5)

# Search button
tk.Button(root, text="Start Screening", command=start_search, bg="blue", fg="black").pack(pady=10)

# Results area
results_text = scrolledtext.ScrolledText(root, height=12, wrap="word", state=tk.DISABLED)
results_text.pack(fill="both", padx=10, pady=5, expand=True)

# Copy button
tk.Button(root, text="Copy Results", command=copy_results).pack(pady=5)

# Run GUI
root.mainloop()
