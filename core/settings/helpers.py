import os

from tools_box.logger.config import configure_app_logging


def configure_logging():
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    NEWRELIC_LOGGING_ENABLED = os.getenv("NEWRELIC_LOGGING_ENABLED", False)
    if ENVIRONMENT == "local":
        configure_app_logging(
            level="DEBUG",
            fmt="rich",
            use_rich=True,
            enable_sql_logging=True,
        )
    else:
        configure_app_logging(
            level="info",
            fmt="json",
            enable_newrelic=NEWRELIC_LOGGING_ENABLED,
            newrelic_service_name="qr",
        )
