# Telegram Shop Bot

A Telegram bot for managing an online shop, built with Python and the following stack:

## Tech Stack

- **aiogram 3.x.x**: Asynchronous framework for building Telegram bots.
- **pydantic**: Data validation and settings management using Python type annotations.
- **alembic**: Database migration tool for SQLAlchemy.

## Bot Commands

The bot supports the following commands:

<p align="center">

<table>
  <thead>
    <tr>
      <th>Command</th>
      <th>Description</th>
      <th>Access</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>/start</code></td>
      <td>Start message to initiate interaction with the bot</td>
      <td><span style="background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">All users</span></td>
    </tr>
    <tr>
      <td><code>/help</code></td>
      <td>List of all available bot commands</td>
      <td><span style="background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">All users</span></td>
    </tr>
    <tr>
      <td><code>/catalog</code></td>
      <td>Displays the catalog of products for sale</td>
      <td><span style="background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">All users</span></td>
    </tr>
    <tr>
      <td><code>/startdialog</code></td>
      <td>Starts a support dialog for user inquiries</td>
      <td><span style="background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">All users</span></td>
    </tr>
    <tr>
      <td><code>/shopcard</code></td>
      <td>Shows the contents of the shopping cart</td>
      <td><span style="background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">All users</span></td>
    </tr>
    <tr>
      <td><code>/myorders</code></td>
      <td>Displays the user's order history</td>
      <td><span style="background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">All users</span></td>
    </tr>
    <tr>
      <td><code>/addproduct</code></td>
      <td>Adds a new product to the catalog</td>
      <td><span style="background-color: #ffebee; color: #c62828; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">Admins only</span></td>
    </tr>
    <tr>
      <td><code>/clearcart</code></td>
      <td>Clears the shopping cart</td>
      <td><span style="background-color: #e1f5fe; color: #0277bd; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">All users</span></td>
    </tr>
    <tr>
      <td><code>/showappeals</code></td>
      <td>Views user support appeals</td>
      <td><span style="background-color: #ffebee; color: #c62828; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">Admins only</span></td>
    </tr>
  </tbody>
</table>

</p>

# Command Examples
Below are example screenshots of the bot's command outputs:

- **/start** <p align="center">
![start command](/assets/images/start.png) </p>

- **/help** <p align="center">
![help command](/assets/images/help.png) </p>

- **/catalog** <p align="center">
![catalog command](/assets/images/catalog.png) </p>

- **/startdialog** <p align="center">
![startdialog command](/assets/images/startdialog.png) </p>

- **/shopcard** <p align="center">
![shopcard command](/assets/images/shopcard.png) </p>

- **/myorders** <p align="center">
![myorders command](/assets/images/myorders.png) </p>


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


6. **Start the bot**:

   ```bash
    uv run main.py
   ```

