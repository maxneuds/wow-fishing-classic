import win32gui

WINDOW_NAME = 'World of Warcraft'
window = win32gui.FindWindow(None, WINDOW_NAME)

if window:
    win32gui.SetForegroundWindow(window)
    left, top, right, bottom = win32gui.GetWindowRect(window)
    print(f"Window position: ({left}, {top}), size: ({right - left}x{bottom - top})")
    frame_rect = win32gui.GetClientRect(window)
    client_left, client_top = win32gui.ClientToScreen(window, (0, 0))
    client_right = client_left + frame_rect[2]
    client_bottom = client_top + frame_rect[3]

    titlebar_height = client_top - top
    border_left = client_left - left
    border_right = right - client_right
    border_bottom = bottom - client_bottom

    print(f"Titlebar height: {titlebar_height}")
    print(f"Left border: {border_left}")
    print(f"Right border: {border_right}")
    print(f"Bottom border: {border_bottom}")
