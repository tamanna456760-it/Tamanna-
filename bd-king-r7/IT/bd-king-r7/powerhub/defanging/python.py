import logging

logger = logging.getLogger("powerhub")
handler = logging.FileHandler("powerhub.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("User login attempt", extra={"ip": request.remote_addr})
