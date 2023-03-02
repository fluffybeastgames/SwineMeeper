import tkinter as tk
import time


    #     self.make_widgets()
    #     self.root.bind('<Return>', self.startstop)
    #     self.root.mainloop()

    # def make_widgets(self):
    #     tk.Label(self.root, textvariable=self.sv, font='ariel 15').pack()

    #     btn_frame = tk.Frame(self.root)
    #     btn_frame.pack()
    #     tk.Button(btn_frame, text='Start', command=self.start).pack(side=tk.LEFT)
    #     tk.Button(btn_frame, text='Stop', command=self.stop).pack(side=tk.RIGHT)

class SwineTimer:
    def __init__(self, root):
        #self.root = tk.Tk()
        self.root = root
        self.timer_label = tk.StringVar()
        self.start_time = None
        self.is_running = False


    def start_timer(self):
        if not self.is_running:
            self.start_time = time.time()
            self.timer()
            self.is_running = True


    def udate_timer_label(self):
        self.timer_label.set(time.time() - self.start_time)
        self.after_loop = self.root.after(50, self.udate_timer_label)


    def pause_timer(self):
        if self.is_running:
            self.timer_label.set(time.time() - self.start_time)
            self.root.after_cancel(self.after_loop)
            self.is_running = False
    
    
    def reset_timer(self):
        if self.is_running:
            self.timer_label.set('000')
            self.root.after_cancel(self.after_loop)
            self.is_running = False


root = tk.Tk()
btn_frame = tk.Frame(root)
btn_frame.pack()

timer = SwineTimer(root)

tk.Button(btn_frame, text='Start', command=timer.start_timer).pack(side=tk.LEFT)
tk.Button(btn_frame, text='Stop', command=timer.pause_timer).pack(side=tk.RIGHT)

root.mainloop()

# class Timer:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.sv = tk.StringVar()
#         self.start_time = None
#         self.is_running = False

#         self.make_widgets()
#         self.root.bind('<Return>', self.startstop)
#         self.root.mainloop()

#     def make_widgets(self):
#         tk.Label(self.root, textvariable=self.sv, font='ariel 15').pack()

#         btn_frame = tk.Frame(self.root)
#         btn_frame.pack()
#         tk.Button(btn_frame, text='Start', command=self.start).pack(side=tk.LEFT)
#         tk.Button(btn_frame, text='Stop', command=self.stop).pack(side=tk.RIGHT)

#     def start(self):
#         if not self.is_running:
#             self.start_time = time.time()
#             self.timer()
#             self.is_running = True

#     def timer(self):
#         self.sv.set(self.format_time(time.time() - self.start_time))
#         self.after_loop = self.root.after(50, self.timer)

#     def stop(self):
#         if self.is_running:
#             self.root.after_cancel(self.after_loop)
#             self.is_running = False

#     def startstop(self, event=None):
#         if self.is_running:
#             self.stop()
#         else:
#             self.start()

#     @staticmethod
#     def format_time(elap):
#         hours = int(elap / 3600)
#         minutes = int(elap / 60 - hours * 60.0)
#         seconds = int(elap - hours * 3600.0 - minutes * 60.0)
#         hseconds = int((elap - hours * 3600.0 - minutes * 60.0 - seconds) * 10)
#         return '%02d:%02d:%02d:%1d' % (hours, minutes, seconds, hseconds)


# Timer()