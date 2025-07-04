# Telegram Shop Bot

A Telegram bot for managing an online shop, built with Python and the following stack:

## Tech Stack

- **aiogram 3.x.x**: Asynchronous framework for building Telegram bots.
- **pydantic**: Data validation and settings management using Python type annotations.
- **alembic**: Database migration tool for SQLAlchemy.

## Bot Commands

The bot supports the following commands:

| Command | Description | Access |
| --- | --- | --- |
| `/start` | Start message to initiate interaction with the bot | All users |
| `/help` | List of all available bot commands | All users |
| `/catalog` | Displays the catalog of products for sale | All users |
| `/startdialog` | Starts a support dialog for user inquiries | All users |
| `/shopcard` | Shows the contents of the shopping cart | All users |
| `/myorders` | Displays the user's order history | All users |
| `/addproduct` | Adds a new product to the catalog | Admins only |
| `/clearcart` | Clears the shopping cart | All users |
| `/showappeals` | Views user support appeals | Admins only |

# Command Examples
Below are example screenshots of the bot's command outputs:

- **/start**
![start command](/assets/images/start.png)
- **/help**
![help command](/assets/images/help.png)
- **/catalog**
![catalog command](/assets/images/catalog.png)
- **/startdialog**
![startdialog command](/assets/images/startdialog.png)
- **/shopcard**
![shopcard command](/assets/images/shopcard.png)
- **/myorders**
![myorders command](/assets/images/myorders.png)


## Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Lanxre/telegram-sales-bot
   cd telegram-sales-bot
   ```

2. **Install dependencies**: Ensure you have Python 3.8+ installed, then run:

   ```bash
   uv install
   ```

3. **Configure environment variables**: Create a `.env` file in the root directory with the following:

   ```
    # TELEGRAM_BOT_TOKEN
    TELEGRAM_BOT_TOKEN=<TELEGRAM_BOT_TOKEN>

    # DATABASE
    DB_NAME=SALES.db
    db_user=admin
    db_password=secret
    db_host=localhost
    db_port=5432
    db_driver=aiosqlite # for sqlite
   ```

4. **Run database migrations**:

   ```bash
   alembic upgrade head
   ```

5. **Change admin id** in [Admin ids located](/admin_ids.txt) and [register in code](/core/infrastructure/__init__.py)
    ```bash
    15. admin_config = AdminConfig(admin_ids=[<You id>])
    ```

6. **Start the bot**:

   ```bash
    uv run main.py
   ```

