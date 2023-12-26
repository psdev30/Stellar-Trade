from loguru import logger

# Configure the logger
logger.add("../logs/app.log", rotation="500 MB", level="DEBUG")

# You can add more configurations as needed

# Create a function to get the logger
def get_logger():
    return logger
