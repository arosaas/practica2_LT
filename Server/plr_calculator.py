from serverSocket import ServerSocket
from Shared.message_builder import build_message, validate_message
import threading

class PLR_calculator_service:
    def __init__(self, logger):
        self.serviceSocket = ServerSocket('127.0.0.1', 32007)
        self.logger = logger
        self.ID = "PLR_CALCULATOR"

    def task(self, message, addr):
        bitstream = message["bitstream"]

        num_zeros = bitstream.count('0')
        num_ones = bitstream.count('1')

        ones = bitstream.split('0')
        bursts = [burst for burst in ones if burst]
        nBursts = len(bursts)

        avg_len = 0

        for burst in bursts:
            avg_len += (len(burst) - 1)

        p = nBursts*1.0/num_zeros
        q = 1 - avg_len*1.0/num_ones
        pi1 = p / (p + q)
        pi0 = 1 - pi1

        result = build_message(
            "PLR_RESPONSE",
            p=p,
            q=q,
            pi1=pi1,
            pi0=pi0,
            E=1/q
        )

        self.serviceSocket.send_message(result, addr)

    def start(self):
        while True:
            message, addr = self.serviceSocket.recv_message(1024)

            if validate_message(message, "PLR_REQUEST"):
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
