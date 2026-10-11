# E-ink Baby Tracker (pregnancy → age)

A simple project that follows a baby from pregnancy to birthdays on a [2.7 inch e-Paper HAT by Waveshare](https://www.waveshare.com/2.7inch-e-paper-hat.htm). Meant to be run on a Raspberry Pi.

| Pregnancy | Age |
|---|---|
| ![Pregnancy screen](docs/screens/pregnancy.png) | ![Age screen](docs/screens/age.png) |
| **Day of birth** | **Birthday** |
| ![Welcome screen](docs/screens/welcome.png) | ![Birthday screen](docs/screens/birthday.png) |

* **Pregnancy** (during the 40 weeks before the expected birth date): completed weeks and days, progress from the moon to the carriage, and the days left. Past the due date it keeps counting and shows how many days overdue.
* **Day of birth:** a welcome screen.
* **Age:** the two largest units of the baby's age, the rest below, and a bar counting down to the next birthday.
* **Birthday:** a celebration screen on every birthday.
* More than 40 weeks before the expected birth date, the screen counts down the days.

The small gray time in the bottom-right corner is when the screen was last refreshed, which makes a stalled device easy to spot.

The screen is in English by default and can be switched to Polish:

| | |
|---|---|
| ![Pregnancy screen in Polish](docs/screens/pregnancy-pl.png) | ![Age screen in Polish](docs/screens/age-pl.png) |

![Completed project photo](docs/completed-project.jpg)

## Setup
1. Configure your Raspberry Pi according to the [docs provided by Waveshare](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT_Manual#Working_With_Raspberry_Pi).
2. Clone this repo:
    ```
    git clone https://github.com/grappeq/e-ink-baby-tracker.git
    ```
3. Install dependencies:
    ```
    pip3 install -r requirements.txt
    ```
4. Install libopenjp2 required by Pillow:
    ```
    sudo apt-get install libopenjp2-7
    ```
5. Copy the `config.json.example` file as `config.json` and fill it in (see below).
6. Configure cron to run the `main.py` file on a schedule, plus once at boot. The Pi has no real-time clock, so give NTP time to sync before the boot run:
    ```
    4 * * * * python3 /home/pi/e-ink-baby-tracker/main.py
    @reboot sleep 90 && python3 /home/pi/e-ink-baby-tracker/main.py
    ```

## Configuration
```json
{
  "expected_birth_date": "2027-01-20",
  "birth_date": null,
  "name": "Zosia",
  "language": "en"
}
```
* `expected_birth_date` – the due date (`YYYY-MM-DD`). The pregnancy is counted as the 280 days before it.
* `birth_date` – the actual birth date. Set it once the baby is born to switch to the age screens. If it's left empty for more than 3 weeks after the due date, the due date is used as the birth date.
* `name` – optional, shown as the title. Without it the title is the birth date.
* `language` – `en` (default) or `pl`.

Either date on its own is enough: a config with only `birth_date` shows the pregnancy before that date.

## Upgrading
This project used to be *e-ink-pregnancy-tracker*. Existing clones keep working (GitHub redirects the old URL) and existing `config.json` files stay valid. After pulling, reinstall the dependencies, because a new one was added:
```
git pull
pip3 install -r requirements.txt
```
Then add `birth_date` to `config.json` when the baby arrives.

## Testing
If you wish to try out the package locally, you can run the `local_test.py` file. The script generates the image and displays it on your screen (or saves it with `--out`) without the need of relying on packages that are available only on Raspberry Pi:
```
python3 local_test.py 2027-01-20 2026-10-11 --name Zosia --lang pl --out preview.png
python3 local_test.py 2024-01-01 2026-10-11 --born 2024-01-01 --out preview.png
```

Run the tests with `python3 -m unittest`.

## Credits
The Nunito font is licensed under the [SIL Open Font License](res/fonts/OFL-Nunito.txt).

## Useful resources
* [2.7 inch e-Paper HAT docs](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT)
* [Model of the case for the display and Raspberry Pi Zero](https://www.printables.com/model/538237-27-inch-e-ink-display-raspberry-pi-zero-case) (visible on the photo above)
