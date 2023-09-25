from tkinter import END

class Logger:
    def __init__(self, console):
        self.console = console
        self.last_log = None

    def print(self, msg):
        if self.last_log != None:
            msg = "\n" + msg
        self.console.insert(END, msg)
        self.console.see(END)
        self.last_log = msg

    def debug(self, msg):
        msg.strip()

        # Extra handling to pretty up the output and stop downloads from flooding the console
        if "[download]" in msg and "[download]" in self.last_log and "Destination" not in self.last_log:
            last = self.console.index("end-1c linestart")
            self.console.delete(last, END)

        self.print(msg if "[" in msg else f"[debug]: {msg}")

    def warning(self, msg):
        self.print(f"[warning]: {msg}")

    def error(self, msg):
        self.print(f"[error]: {msg}")