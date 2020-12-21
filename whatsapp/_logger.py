"""A logger module used to log the Whatsapp Client.
"""

import logging
import inspect
import typing
import whatsapp.message


class Logger:
    """A logger used to log the Whatsapp Client.
    """

    def __init__(self) -> None:
        self.__logger = logging
        self.__level = logging.INFO
        self.__logger.basicConfig(level=logging.INFO, format="[%(asctime)s] - [Whatsapp] - %(levelname)s - %(message)s")
        self.__logger.info("Logger set.")

    def __str__(self) -> str:
        string = f"A Whatsapp logger. Log level: {self.__level}"
        return string

    def log_command(self, command: str, command_function: typing.Callable) -> None:
        """Logs a command.

        Args:
            command (str): the command name.
            command_function (typing.Callable): the command function.
        """
        f_name = command_function.__name__
        f_file = inspect.getfile(command_function)
        self.__logger.info(f"Executing command {command}. (Command function {f_name}, file {f_file}.)")

    def log_msg_listener(self, msg_function: typing.Callable, msg: whatsapp.message.Message) -> None:
        """Logs a message listener.

        Args:
            msg_function (typing.Callable): the message listener.
            msg (whatsapp.message.Message): the message object.
        """
        f_name = msg_function.__name__
        f_file = inspect.getfile(msg_function)
        self.__logger.info(f"Executing on_message listener on message {msg}. (Function {f_name}, file {f_file}.)")

    def log(self, log_level: typing.Literal[20, 30, 40], msg: str) -> None:
        """Logs a message.

        Args:
            log_level (typing.Literal[20, 30, 40]): the log level.
            msg (str): the message.
        """
        self.__logger.log(level=log_level, msg=msg)

    @property
    def log_level(self):
        """Log level property.
        """
        return self.__level

    @log_level.setter
    def log_level(self, lvl: typing.Literal[20, 30, 40]) -> None:
        """Log level setter.
        """
        self.__level = lvl
        self.__logger.basicConfig(level=lvl)

    def log_error(self, exception: Exception, executing: str) -> None:
        """Logs an error.

        Args:
            exception (Exception): the exception.
            executing (str): what the program was executing.
        """
        self.__logger.error(f"Exception occurred while executing {executing}:", exc_info=exception)

    def log_warning(self, exception: Exception, executing: str) -> None:
        """Logs a warning.

        Args:
            exception (Exception): the exception.
            executing (str): what the program was executing.
        """
        self.__logger.warning(f"Exception occurred while executing {executing}:", exc_info=exception)
