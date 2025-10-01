# Telegram Self-Bot as Web Service on Render

This is a Telegram self-bot built with Pyrogram, integrated with a FastAPI web server to run as a web service on Render. The bot responds to the `.chk` command to fetch mobile information.

## Prerequisites
- A Telegram account with API credentials from [my.telegram.org](https://my.telegram.org).
- A Render account for deployment.

## Setup Instructions
1. **Fork or Clone the Repository**
   - Clone this repository to your local machine or fork it on GitHub.

2. **Set Up Environment Variables**
   - In Render, create a new **Web Service**.
   - Add the following environment variables in the Render dashboard:
     - `TELEGRAM_API_ID`: Your Telegram API ID.
     - `TELEGRAM_API_HASH`: Your Telegram API Hash.
     - `SESSION_NAME`: (Optional) Name of the session, defaults to `selfbot`.
     - `PORT`: (Optional) Port for the web server, defaults to `8000`. Render assigns a port automatically.

3. **Deploy on Render**
   - Connect your repository to Render.
   - Select the repository and branch to deploy.
   - Ensure the **Runtime** is set to `Python 3`.
   - Set the **Build Command** to:
