"""Launch the Retail Sales Analytics Dashboard."""

from dashboard import DashboardApp


def main():
    import tkinter as tk

    root = tk.Tk()
    DashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
