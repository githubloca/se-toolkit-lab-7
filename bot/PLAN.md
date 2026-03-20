# Development Plan for Telegram Bot

This plan outlines the steps for building a testable Telegram bot integrated with the LMS backend.

1. **Architecture:** We use a modular approach where handlers are decoupled from the Telegram transport layer. This ensures that logic can be tested independently of the Telegram API using the --test flag.
2. **Scaffolding:** Using 'uv' for dependency management provides a fast and reliable environment. The project structure includes 'handlers/' for logic and 'services/' for API interactions.
3. **Backend Integration:** In the next tasks, we will implement service clients to communicate with the LMS API. These services will handle authentication using keys from environment variables.
4. **Intent Routing:** The bot will support both explicit commands (like /start) and natural language queries using an LLM-based routing system.
5. **Deployment:** The bot will be deployed on the VM using 'nohup' or a process manager to ensure it stays online and responds to user requests in real-time.

## Project Structure Overview
The project is organized into several key directories to ensure clean separation of concerns. 
- The 'handlers' directory contains the logic for processing user commands like /start and /help. 
- The 'services' directory is reserved for external API communications, such as fetching data from the LMS backend. 
- The 'config.py' file handles environment variables securely using the python-dotenv library.
- The 'bot.py' entry point manages the lifecycle of the application, switching between CLI test mode and the live Telegram polling mode.
This modular approach allows for easier debugging and ensures that the core logic remains independent of the Telegram transport layer.
