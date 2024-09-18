# us-visa

## Setup

1. **Install Dependencies**:

   - Ensure you have Python installed.
   - Install the required Python packages:

   ```sh
   pip install selenium requests schedule
   pip install python-dotenv
   ```

2. **Configure**:

   - Update the [`config.py`] file with your email, password, Telegram token, chat IDs, and other necessary configurations.

3. **Download ChromeDriver**:
   - Ensure you have the correct version of ChromeDriver that matches your Chrome browser version.
   - [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/#stable)
   - Place the `chromedriver.exe` in the [`chromedriver-win64`] directory on root folder.

## Usage

Run the script to start checking for available visa appointment dates and receive notifications via Telegram:

```sh
python start.py
```
