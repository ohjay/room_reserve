# `room_reserve`

Book a study room via Python script.

## Supported libraries
(any other libraries have not been tested)

- Moffitt

## Dependencies
- Google Chrome
- Python 2.7
- Selenium (`pip install selenium`)
- PyYAML (`pip install pyyaml`)

## Getting started
1. Download the appropriate Chrome driver [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).
2. Edit the config file. You will need to provide the URL for room reservations, your booking information (room, time, etc.), and your CalNet credentials.
3. Make sure your physical cursor is out of the way (ideally on the edge of the screen).

Run the following command:
```
python main.py -cfg <path to config.yaml> -c <path to chromedriver>
```

## Configuration
- `start_time`: desired booking time in military format
- `room`: room number (within library)
- `midnight_launch`: wait until midnight (i.e. the start of the next day) to reserve the room
