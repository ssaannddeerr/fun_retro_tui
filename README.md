# 🖥️ Retro TUI Launcher

A nostalgic terminal user interface launcher with a retro ASCII welcome animation and modern application integration. Features real-time weather updates, cryptocurrency tracking, and easy access to various terminal-based applications.

![Main Interface](main_interface.png)

## ✨ Features

### Welcome Animation
- Beautiful ASCII art animation spelling "WELCOME"
- Color-cycling effects
- Smooth loading spinner
- Centered display with dynamic terminal sizing

### Main Interface
- Retro-styled ASCII art title "APPLE"
- Grid-based application launcher with 3-column layout
- Real-time status information:
  - Current time and date
  - Local weather conditions
  - Bitcoin price tracker
  - Exchange rate
- Vim-style navigation (hjkl and arrow keys)

## 🚀 Installation

### Prerequisites
- Python 3.7+
- pip3
- Unix-like operating system (Linux/BSD/macOS)

### Required Python Packages
```bash
pip3 install prompt_toolkit requests pytz
```

### Required Applications
```bash
# For various launcher functions
sudo apt install ncspot mpv newsboat lynx curl ncal
```

## 📱 Integrated Applications

1. **Claude AI**
   - AI chat interface
   - Custom shell script integration

2. **Media Applications**
   - YouTube terminal viewer (via [yt-x](https://github.com/Benexl/yt-x))
   - Spotify (via ncspot)
   - Live TV Streams (via mpv)

4. **Information Tools**
   - [Newsboat](https://github.com/newsboat/newsboat) RSS reader (password protected)
   - [Lynx](https://lynx.invisible-island.net/) web browser
   - Moon phase viewer
   - Weather display
   - Calendar view
  
![Moon Applet Screenshot](moon_applet.png)

## ⌨️ Controls

- `↑` or `k`: Move selection up
- `↓` or `j`: Move selection down
- `←` or `h`: Move selection left
- `→` or `l`: Move selection right
- `Enter`: Launch selected application
- `q`: Quit launcher

## 🔄 Real-time Updates

The launcher includes several background threads that automatically update:
- Weather conditions (every 15 minutes)
- Bitcoin price (every minute)
- Exchange rate (hourly)

## 🔒 Security Features

Some applications (like News) are password-protected and require authentication before launch.

## 🎨 UI Elements

The interface features:
- Retro-styled ASCII borders
- Highlighted selection boxes
- Color-coded information panels
- Real-time status bar
- Centered layout with dynamic terminal sizing

## 🛠️ Configuration

The launcher uses environment-specific configurations for:
- Application paths
- API endpoints for weather, cryptocurrency, and exchange rates
- Protected application passwords
- Default location for weather

## 📝 Notes

- The weather information uses wttr.in
- Currency rates are fetched from exchangerate-api.com
- Bitcoin prices are retrieved from CoinGecko's API
- All live streams require a valid URL that can be played with mpv
- The launcher is designed to work best [cool-retro-term](https://github.com/Swordfish90/cool-retro-term)

## 🚫 Requirements

The launcher requires a terminal that supports:
- Unicode characters
- ANSI color codes
- Minimum terminal size to accommodate the UI layout
