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

## Usage

Run the script to start checking for available visa appointment dates and receive notifications via Telegram:

```sh
python start.py
```
