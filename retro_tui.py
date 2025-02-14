#!/usr/bin/env python3
import time
import os
import shutil
import itertools
import subprocess
import datetime
import requests
import threading
import pytz

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import print_formatted_text, Application
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, FloatContainer, Float
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.keys import Keys


# ----------------- loading_welcome.py -----------------
class WelcomeAnimation:
    def __init__(self):
        # Store each letter's frames
        self.letters = {
            'W': [
                "██╗    ██╗",
                "██║    ██║",
                "██║ █╗ ██║",
                "██║███╗██║",
                "╚███╔███╔╝",
                " ╚══╝╚══╝ "
            ],
            'E': [
                "███████╗",
                "██╔════╝",
                "█████╗  ",
                "██╔══╝  ",
                "███████╗",
                "╚══════╝"
            ],
            'L': [
                "██╗     ",
                "██║     ",
                "██║     ",
                "██║     ",
                "███████╗",
                "╚══════╝"
            ],
            'C': [
                " ██████╗",
                "██╔════╝",
                "██║     ",
                "██║     ",
                "╚██████╗",
                " ╚═════╝"
            ],
            'O': [
                " ██████╗ ",
                "██╔═══██╗",
                "██║   ██║",
                "██║   ██║",
                "╚██████╔╝",
                " ╚═════╝ "
            ],
            'M': [
                "███╗   ███╗",
                "████╗ ████║",
                "██╔████╔██║",
                "██║╚██╔╝██║",
                "██║ ╚═╝ ██║",
                "╚═╝     ╚═╝"
            ]
        }

        self.word = "WELCOME"
        self.colors = ['ansired', 'ansiyellow', 'ansigreen', 'ansiblue', 'ansimagenta']
        self.pulse_chars = ["░", "▒", "▓", "█"]

        # Loading animation characters
        self.loading_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

        # Get terminal size
        self.terminal_size = shutil.get_terminal_size()
        self.terminal_width = self.terminal_size.columns
        self.terminal_height = self.terminal_size.lines

        # Calculate total width of the word
        self.total_width = sum(len(self.letters[letter][0]) for letter in self.word) + len(self.word) - 1

        # Calculate padding for centering
        self.left_padding = (self.terminal_width - self.total_width) // 2
        # Adjusted top padding to leave room for loading text
        self.top_padding = (self.terminal_height - 10) // 2  # Increased space for loading text

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_centered_frame(self, current_letters, color='ansired', pulse_char='█', loading_char='⠋'):
        # Print top padding
        for _ in range(self.top_padding):
            print()

        # Create empty frame with correct height
        frame = ["" for _ in range(6)]

        # Build each line of the frame
        for i in range(6):
            # Add left padding
            frame[i] = " " * self.left_padding

            # Add each letter
            for idx, letter in enumerate(self.word):
                if idx < len(current_letters):
                    # Replace █ with pulse_char in the current letter's frame
                    letter_frame = self.letters[letter][i].replace('█', pulse_char)
                    frame[i] += letter_frame
                    # Add space between letters
                    if idx < len(self.word) - 1:
                        frame[i] += " "
                else:
                    # Add empty space for letters not yet revealed
                    frame[i] += " " * (len(self.letters[letter][0]))
                    if idx < len(self.word) - 1:
                        frame[i] += " "

        # Print the frame
        for line in frame:
            print_formatted_text(HTML(f'<{color}>{line}</{color}>'))

        # Add some spacing
        print("\n")

        # Print centered loading text with spinner
        loading_text = f"Loading {loading_char}"
        loading_padding = " " * ((self.terminal_width - len(loading_text)) // 2)
        print_formatted_text(HTML(f'<ansigray>{loading_padding}{loading_text}</ansigray>'))

    def animate(self):
        self.clear_screen()
        loading_spinner = itertools.cycle(self.loading_chars)

        # Letter by letter animation
        for letter_count in range(len(self.word) + 1):
            current_letters = self.word[:letter_count]

            # Pulse and color animation for each new letter
            if letter_count > 0:
                # Only one color cycle per letter
                for color in self.colors[:2]:  # Reduced to just 2 colors per letter
                    # Faster pulse animation
                    for pulse_char in self.pulse_chars:
                        self.clear_screen()
                        self.print_centered_frame(current_letters, color, pulse_char, next(loading_spinner))
                        time.sleep(0.02)  # Reduced from 0.05

            # Shorter pause between letters
            time.sleep(0.05)  # Reduced from 0.1

        # Final flourish - one full color cycle
        for color in self.colors:
            self.clear_screen()
            self.print_centered_frame(self.word, color, '█', next(loading_spinner))
            time.sleep(0.1)

        # Hold the final state for 1.5 seconds, but keep spinner moving
        start_time = time.time()
        while time.time() - start_time < 5:
            self.clear_screen()
            self.print_centered_frame(self.word, 'ansired', '█', next(loading_spinner))
            time.sleep(0.1)


# ----------------- tui_launcher_2025_21.py -----------------
class AppLauncher:
    def __init__(self):
        self.should_exit = False  # Initialize this first
        self.protected_apps = {
            "News": "asdf"  # News requires password "1234"
        }
        self.selected = 0
        self.kb = KeyBindings()
        self.setup_keybindings()
        self.apps = [
            ("Claude AI", "sh AICHAT SCRIPT"),
            ("Spotify", "ncspot"),
            ("CNN Live", "mpv -fs URL"),
            ("News", "newsboat -r"),
            ("YouTube", "yt-x"),
            ("FoxNews Live", "mpv -fs URL"),
            ("Web Browser", "lynx"),
            ("Moon Phase", "curl wttr.in/moon"),
            ("BBC Live", "mpv -fs URL"),
            ("Weather", "curl wttr.in/Prague?2n"),
            ("Calendar", "ncal -C 2025"),
            ("NHK Live", "mpv -fs URL"),
        ]
        self.weather = self.get_weather()
        self.bitcoin_price = self.get_bitcoin_price()
        self.czk_rate = self.get_czk_rate()

        # Start threads after all attributes are initialized
        self.start_weather_update_thread()
        self.start_bitcoin_update_thread()
        self.start_czk_update_thread()

    def start_weather_update_thread(self):
        def update_weather():
            while not self.should_exit:
                try:
                    self.weather = self.get_weather()
                except Exception as e:
                    self.weather = "Weather unavailable"
                time.sleep(900)  # 15 minutes

        thread = threading.Thread(target=update_weather, daemon=True)
        thread.start()

    def setup_keybindings(self):
        @self.kb.add(Keys.Any)
        def _(event):
            key = event.key_sequence[0].key
            self.handle_key(key, event.app)
            event.app.invalidate()

    def handle_key(self, key, app):
        if key == 'q':
            self.should_exit = True
            app.exit()
        elif key in (Keys.Up, 'k'):
            self.selected = (self.selected - 3) % len(self.apps)
        elif key in (Keys.Down, 'j'):
            self.selected = (self.selected + 3) % len(self.apps)
        elif key in (Keys.Right, 'l'):
            if self.selected % 3 != 2:
                self.selected = (self.selected + 1) % len(self.apps)
        elif key in (Keys.Left, 'h'):
            if self.selected % 3 != 0:
                self.selected = (self.selected - 1) % len(self.apps)
        elif key == Keys.Enter:
            app.exit()  # Just exit the TUI, we'll handle the launch in run()

    def get_app_button(self, app_name, index):
        button_width = 20
        padding = (button_width - len(app_name)) // 2
        left_padding = ' ' * padding
        right_padding = ' ' * (button_width - len(app_name) - padding)

        if index == self.selected:
            text = HTML(f'<reverse>╔{"═" * button_width}╗\n'
                        f'║{left_padding}<b>{app_name}</b>{right_padding}║\n'
                        f'╚{"═" * button_width}╝</reverse>')
        else:
            text = HTML(f'╔{"═" * button_width}╗\n'
                        f'║{left_padding}{app_name}{right_padding}║\n'
                        f'╚{"═" * button_width}╝')

        return text

    def get_retro_title(self, width):
        title = [
            "  █████╗ ██████╗ ██████╗ ██╗     ███████╗",
            " ██╔══██╗██╔══██╗██╔══██╗██║     ██╔════╝",
            " ███████║██████╔╝██████╔╝██║     █████╗  ",
            " ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝  ",
            " ██║  ██║██║     ██║     ███████╗███████╗",
            " ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝"
        ]
        title_width = len(title[0])
        left_padding = (width - title_width - 2) // 2  # -2 for the border characters

        centered_title = [f'{" " * left_padding}╔{"═" * (title_width + 2)}╗\n']
        for line in title:
            centered_title.append(f'{" " * left_padding}║ {line} ║\n')
        centered_title.append(f'{" " * left_padding}╚{"═" * (title_width + 2)}╝')

        return HTML('<ansired>' + ''.join(centered_title) + '</ansired>')

    def get_clock_and_date(self):
        prague_tz = pytz.timezone('Europe/Prague')  # Prague uses CET/CEST
        now = datetime.datetime.now(pytz.UTC).astimezone(prague_tz)
        return now.strftime("%B %d, %Y %H:%M:%S %Z")  # %Z will show CET or CEST accordingly

    def get_weather(self):
        try:
            response = requests.get('https://wttr.in/Prague?format=%C+%t&u')  # Added &m for metric (Celsius)
            if response.status_code == 200:
                return response.text.strip()
            else:
                return "Weather unavailable"
        except:
            return "Weather unavailable"

    def get_bitcoin_price(self):
        try:
            # Use CoinGecko's public API
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd')
            if response.status_code == 200:
                data = response.json()
                price = data.get("bitcoin", {}).get("usd")
                if price:
                    return f"BTC: ${price:,.2f}"
                else:
                    return "BTC: Data Unavailable"
            else:
                return "BTC: API Error"
        except requests.exceptions.RequestException:
            return "BTC: Connection Error"

    def get_czk_rate(self):
        try:
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
            if response.status_code == 200:
                data = response.json()
                rate = data['rates'].get('CZK')
                if rate:
                    return f"1 USD = {rate:.2f} CZK"
                else:
                    return "CZK: Data Unavailable"
            else:
                return "CZK: API Error"
        except requests.exceptions.RequestException:
            return "CZK: Connection Error"

    def start_czk_update_thread(self):
        def update_czk_rate():
            while not self.should_exit:
                self.czk_rate = self.get_czk_rate()
                time.sleep(3600)  # Update every hour (3600 seconds)

        thread = threading.Thread(target=update_czk_rate, daemon=True)
        thread.start()

    def start_bitcoin_update_thread(self):
        def update_bitcoin_price():
            while not self.should_exit:
                self.bitcoin_price = self.get_bitcoin_price()
                time.sleep(60)  # Wait for 60 seconds

        thread = threading.Thread(target=update_bitcoin_price, daemon=True)
        thread.start()

    def get_info_panel(self, text, index):
        button_width = 20
        text = text[:button_width - 2]  # Truncate text if it's too long
        padding = (button_width - len(text)) // 2
        left_padding = ' ' * padding
        right_padding = ' ' * (button_width - len(text) - padding)

        panel = HTML(f'╔{"═" * button_width}╗\n'
                     f'║{left_padding}<ansicyan>{text}</ansicyan>{right_padding}║\n'
                     f'╚{"═" * button_width}╝')

        return panel

    def get_status_bar(self):
        return VSplit([
            Window(content=FormattedTextControl(lambda: HTML(f'<ansigreen>{self.get_clock_and_date()}</ansigreen>')),
                   align='left'),
            Window(content=FormattedTextControl(' '), width=1),  # 1-space separator
            Window(content=FormattedTextControl(lambda: HTML(f'<ansiyellow>{self.weather}</ansiyellow>')),
                   align='right', width=len(self.weather) + 1)
        ])

    def run_app(self):
        def create_button_window(index):
            return Window(
                content=FormattedTextControl(lambda: self.get_app_button(self.apps[index][0], index)),
                height=3,
                width=22
            )

        def create_info_panel_window(text, index):
            return Window(
                content=FormattedTextControl(lambda: self.get_info_panel(text, index)),
                height=3,
                width=22
            )

        button_grid = VSplit([
            HSplit([create_button_window(i) for i in range(0, len(self.apps), 3)]),
            Window(width=4),  # Space between columns
            HSplit([create_button_window(i) for i in range(1, len(self.apps), 3)]),
            Window(width=4),  # Space between columns
            HSplit([create_button_window(i) for i in range(2, len(self.apps), 3)]),
        ])

        info_panels = VSplit([
            create_info_panel_window(self.bitcoin_price, 0),
            Window(width=4),  # Space between panels
            create_info_panel_window(self.czk_rate, 1),  # Show CZK rate instead of placeholder
        ])

        main_content = HSplit([
            Window(content=FormattedTextControl(lambda: self.get_retro_title(self.app.output.get_size().columns)),
                   height=8),
            Window(height=2, style="class:background"),  # 4 lines of spacing
            VSplit([
                Window(style="class:background", width=lambda: (self.app.output.get_size().columns - 74) // 2),
                button_grid,
                Window(style="class:background", width=lambda: (self.app.output.get_size().columns - 74) // 2),
            ]),
            Window(height=1, style="class:background"),  # 1 line of spacing
            VSplit([
                Window(style="class:background", width=lambda: (self.app.output.get_size().columns - 48) // 2),
                info_panels,
                Window(style="class:background", width=lambda: (self.app.output.get_size().columns - 48) // 2),
            ]),
        ])

        status_bar = self.get_status_bar()

        root_container = FloatContainer(
            content=HSplit([
                main_content,
                Window(style="class:background"),  # This will expand to fill available space
            ]),
            floats=[
                Float(
                    content=status_bar,
                    bottom=0,
                    left=0,
                    right=0,
                    height=1
                )
            ]
        )

        layout = Layout(root_container)

        style = Style.from_dict({
            'window': 'bg:#000000 #ffffff',
            'background': 'bg:#000000',
        })

        self.app = Application(
            layout=layout,
            key_bindings=self.kb,
            style=style,
            full_screen=True,
            refresh_interval=1  # Refresh every second for the clock
        )

        self.app.run()

    def run(self):
        while not self.should_exit:
            self.run_app()
            if not self.should_exit:
                app_name, command = self.apps[self.selected]

                # Check if app is password protected
                if app_name in self.protected_apps:
                    os.system('clear')
                    password = input(f"Enter password for {app_name}: ")
                    if password != self.protected_apps[app_name]:
                        print("Incorrect password.")
                        input("Press Enter to continue...")
                        continue  # Go back to the TUI without launching the app

                # If we get here, either the app isn't protected or the password was correct
                os.system('clear')  # Clear the terminal before launching the app
                subprocess.call(command, shell=True)
                input("\nPress Enter to return to the TUI...")
                self.weather = self.get_weather()  # Update weather when returning to the launcher


# ----------------- Main Execution -----------------
if __name__ == "__main__":
    # Run welcome animation first (DO NOT MODIFY THE DESIGN)
    animation = WelcomeAnimation()
    animation.animate()

    # Then launch the TUI launcher
    AppLauncher().run()
