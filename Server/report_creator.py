import threading

from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class Report_creator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32008)
        self.logger = logger
        self.ID = "REPORT_CREATOR"

    def task(self, message, addr):
        pass

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            if validate_message(message, "REPORT_REQUEST"):
                self.logger.info(f"{self.ID}: Valid message received")
                self.logger.info(message)

                thread = threading.Thread(
                    target=self.task,
                    args=(message, addr),
                    daemon=True
                )

                thread.start()
            else:
                self.logger.error(f"{self.ID}: Wrong message received")
                pass

    def close(self):
        self.serviceSocket.close()
