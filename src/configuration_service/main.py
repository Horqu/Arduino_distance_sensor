import wx
import wx.lib.intctrl
import serial
import threading
import datetime

logs = [] 
ser = serial.Serial('COM3', 9600)

def get_timestamp_no_space():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

log_parking = False
parking_iteration = 1
log_file_date = get_timestamp_no_space()
log_file_name = "logs_" + log_file_date + ".txt"
last_close_distance_value = 0
last_far_distance_value = 0

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]

def start_parking(event):
    global log_parking
    log_parking = True

def stop_parking(event):
    global log_parking
    global parking_iteration
    if log_parking:
        log_parking = False
        parking_iteration += 1

def read_from_arduino():
    while True:
        if ser.in_waiting and log_parking:
            line = ser.readline().decode('utf-8').rstrip()
            logs.append(f"[{get_timestamp()}] Distance: {line}, Parking no. {parking_iteration}")
            wx.CallAfter(update_logs)

def send_config(event):
    global last_close_distance_value
    global last_far_distance_value

    close_distance = input_1.GetValue()
    input_1.Clear()
    input_1.SetValue(0)
    far_distance = input_2.GetValue()
    input_2.Clear()
    input_2.SetValue(0)

    if (last_close_distance_value == close_distance and last_far_distance_value == far_distance) or (close_distance == 0 or far_distance == 0):
        return
    
    if (close_distance > far_distance):
        return
    
    config = str(close_distance) + "," + str(far_distance)
    logs.append(f"[{get_timestamp()}] Config has ben changed: close_distance={close_distance if close_distance != 0 else last_close_distance_value} , far_distance={far_distance if far_distance != 0 else last_far_distance_value}")
    
    
    if close_distance != last_close_distance_value and close_distance != 0:
        last_close_distance_value = close_distance
    if far_distance != last_far_distance_value and far_distance != 0:
        last_far_distance_value = far_distance
    update_logs()
    ser.write(config.encode())

def update_logs():
    log_text = "\n".join(logs)
    log_window.SetValue(log_text)
    log_window.ShowPosition(log_window.GetLastPosition())
    with open(log_file_name, "w") as file:
        file.write(log_text)


app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "Configuration", size=(800, 600))

panel = wx.Panel(frame)

main_sizer = wx.BoxSizer(wx.VERTICAL)
grid = wx.GridBagSizer(5, 5)

# button z close_distance
label_1 = wx.StaticText(panel, label="close_distance:")
grid.Add(label_1, pos=(1, 0), flag=wx.ALIGN_CENTER_VERTICAL)
input_1 = wx.lib.intctrl.IntCtrl(panel, size=(200, -1), value=0)
grid.Add(input_1, pos=(1, 1), flag=wx.EXPAND)

# button z far_distance
label_2 = wx.StaticText(panel, label="far_distance:")
grid.Add(label_2, pos=(2, 0), flag=wx.ALIGN_CENTER_VERTICAL)
input_2 = wx.lib.intctrl.IntCtrl(panel, size=(200, -1))
grid.Add(input_2, pos=(2, 1), flag=wx.EXPAND)

# button do wysylania konfiguracji
button = wx.Button(panel, label="Send")
button.Bind(wx.EVT_BUTTON, send_config)
grid.Add(button, pos=(3, 0), span=(1, 2), flag=wx.EXPAND)

button_start_parking = wx.Button(panel, label="Start parking")
button_start_parking.Bind(wx.EVT_BUTTON, start_parking)
grid.Add(button_start_parking, pos=(4, 0), span=(0, 2), flag=wx.EXPAND)

button_stop_parking = wx.Button(panel, label="Finish parking")
button_stop_parking.Bind(wx.EVT_BUTTON, stop_parking)
grid.Add(button_stop_parking, pos=(5, 0), span=(0, 2), flag=wx.EXPAND)

# Okno logów
main_sizer.Add(grid, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
main_sizer.AddSpacer(40)
logs_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
logs_label = wx.StaticText(panel, pos=(5,0), label="Logs:")
logs_label_sizer.Add(logs_label, flag=wx.ALIGN_LEFT)
main_sizer.Add(logs_label_sizer, flag=wx.EXPAND | wx.LEFT, border=10)
log_window = wx.TextCtrl(panel,style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
main_sizer.Add(log_window, 1, wx.EXPAND | wx.ALL, 5) 

panel.SetSizer(main_sizer)
frame.Show()

# Uruchomienie wątku do nasłuchiwania Arduino
thread = threading.Thread(target=read_from_arduino, daemon=True)
thread.start()
app.MainLoop()


