import win32api
import win32gui
import tkinter
import time
import asyncio
import ctypes

# identifier of insert cursor
INSERT_CURSOR = 65541

# supported languages;
# codes could added from
# https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/a9eac961-e77d-41a6-90a5-ce1a8b0cdb9c?redirectedfrom=MSDN
languages = {
    '0x409': "EN",
    '0x419': "RU",
    '0x422': "UA"
}


class Tooltip:
    """Tooltip with layout language"""
    label = None
    showed = False
    font = (None, '30')
    fg = 'black'
    bg = 'white'

    def show(self, top, left):
        if not self.label:
            self.label = tkinter.Label(text="*", font=self.font, fg=self.fg, bg=self.bg, cursor="hand1")
            self.label.master.overrideredirect(True)
            self.label.master.geometry(f"+{top + 20}+{left + 20}")
            self.label.master.wm_attributes("-topmost", True)
            self.label.master.wm_attributes("-disabled", True)
            self.label.master.lift()
            self.label.pack()
            self.label.bind("<Button-1>", lambda e: self.hide())
            self.label.update()

    def hide(self):
        if self.label:
            self.label.pack_forget()
            self.label.update()
            self.label.master.destroy()
            self.label = None

    def set(self, text):
        if self.label:
            self.label.config(text=text)
            self.label.update()


def get_layout():
    """Get current keyboard layout"""
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    handle = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(handle, 0)
    layout_id = user32.GetKeyboardLayout(thread_id)
    language_id = layout_id & (2 ** 16 - 1)
    language_id_hex = hex(language_id)

    if language_id_hex in languages.keys():
        return languages[language_id_hex]
    else:
        return "??"


async def main_loop():
    """Main loop.

    Check if left mouse button pressed.
    If so - checks if cursor has "insert" type.
    If so - gets current layout and shows tooltip.
    If left mouse button click occurs with any other type of cursor -
    hides the tooltip;
    Also hides the tooltip if clicked on it.
    """
    current_lmb_state = win32api.GetKeyState(0x01)
    current_layout = None
    tooltip = Tooltip()
    while True:  # main loop
        lmb_state = win32api.GetKeyState(0x01)
        if lmb_state != current_lmb_state:  # mouse button state changed
            current_lmb_state = lmb_state
            if lmb_state < 0:  # button is pressed
                _, cursor_type, (top, left) = win32gui.GetCursorInfo()  # get cursor type and position
                if cursor_type == INSERT_CURSOR:
                    tooltip.show(top, left)  # prepare tooltip to be shown
                else:
                    current_layout = None
                    tooltip.hide()
        if tooltip and tooltip.label:  # loop to refresh layout info if tooltip showed
            tooltip.label.update()
            layout = get_layout()
            if layout != current_layout:
                current_layout = layout
                tooltip.set(layout)
        time.sleep(0.001)


asyncio.get_event_loop().run_until_complete(main_loop())
