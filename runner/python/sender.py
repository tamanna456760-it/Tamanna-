"""
Satellite Sender Module

This module provides a Sender class for encoding, modulating, and transmitting
signals to a satellite. Designed to be extensible for various physical layers,
modulation schemes, and forward error correction.
"""

import logging
import math
import random
from dataclasses import dataclass
from typing import Any, List, Optional

# Configure module-level logger
logger = logging.getLogger(__name__)


@dataclass
class TransmissionParameters:
    """Parameters describing a transmission."""
    frequency_hz: float
    power_dbm: float
    modulation: str  # e.g., "BPSK", "QPSK"
    data_rate_bps: float


class Sender:
    """
    A generic satellite signal transmitter.

    Handles data encoding, framing, modulation, and transmission.
    This implementation is a placeholder and can be extended for specific
    modulation schemes (BPSK, QPSK, etc.) and protocols (AX.25, CCSDS, etc.).
    """

    def __init__(
        self,
        center_freq_hz: float,
        sample_rate_hz: float,
        power_dbm: float = 20.0,
        modulation: str = "BPSK",
        use_hardware: bool = False
    ):
        """
        Initialize the sender.

        Args:
            center_freq_hz: Center frequency for transmission in Hz.
            sample_rate_hz: Sample rate in samples per second (IQ).
            power_dbm: Transmission power in dBm.
            modulation: Modulation scheme (e.g., "BPSK", "QPSK").
            use_hardware: If True, attempt to use real SDR hardware;
                          otherwise simulated (no actual RF output).
        """
        self.center_freq_hz = center_freq_hz
        self.sample_rate_hz = sample_rate_hz
        self.power_dbm = power_dbm
        self.modulation = modulation
        self.use_hardware = use_hardware

        # Placeholder for hardware backend (e.g., HackRF, PlutoSDR)
        self._sdr = None

        if use_hardware:
            logger.info("Hardware mode selected, but no SDR backend implemented.")
            # In a real implementation, initialize like:
            # from hackrf import HackRF
            # self._sdr = HackRF()
            # self._sdr.sample_rate = sample_rate_hz
            # self._sdr.center_freq = center_freq_hz
            # self._sdr.tx_gain = power_dbm_to_gain(power_dbm)
        else:
            logger.info("Sender in simulation mode (no RF output).")

    def set_frequency(self, frequency_hz: float) -> None:
        """
        Change the transmission center frequency.

        Args:
            frequency_hz: New center frequency in Hz.
        """
        self.center_freq_hz = frequency_hz
        if self._sdr is not None:
            # self._sdr.center_freq = frequency_hz
            pass
        logger.debug(f"Transmit frequency set to {frequency_hz} Hz")

    def set_power(self, power_dbm: float) -> None:
        """
        Set the transmission power.

        Args:
            power_dbm: Power in dBm.
        """
        self.power_dbm = power_dbm
        if self._sdr is not None:
            # self._sdr.tx_gain = power_dbm_to_gain(power_dbm)
            pass
        logger.debug(f"Transmit power set to {power_dbm} dBm")

    def send(self, data: bytes, duration_sec: Optional[float] = None) -> bool:
        """
        Encode, modulate, and transmit data.

        Args:
            data: Raw bytes to send.
            duration_sec: Optional; if provided, ensures transmission fits duration.
                          Otherwise computed based on data rate.

        Returns:
            True if transmission succeeded (or simulated), False on error.
        """
        if not data:
            logger.warning("No data to send")
            return False

        logger.info(f"Sending {len(data)} bytes at {self.center_freq_hz} Hz")

        # Step 1: Encode data with framing
        framed_bits = self._encode(data)
        if not framed_bits:
            logger.error("Encoding failed")
            return False

        # Step 2: Modulate bits into IQ samples
        samples = self._modulate(framed_bits)
        if samples is None or len(samples) == 0:
            logger.error("Modulation failed")
            return False

        # Step 3: Transmit samples
        success = self._transmit(samples, duration_sec)
        if success:
            logger.info("Transmission completed")
        else:
            logger.error("Transmission failed")

        return success

    def _encode(self, data: bytes) -> List[int]:
        """
        Encode raw data into a stream of bits with framing.

        Adds a simple preamble (0xAA, 0xBB) and a length header.
        Placeholder: no forward error correction.

        Args:
            data: Raw bytes.

        Returns:
            List of integer bits (0/1).
        """
        bits = []
        # Preamble: 10101010 10111011 (0xAA, 0xBB)
        preamble = [0xAA, 0xBB]
        for byte in preamble:
            for i in range(7, -1, -1):  # MSB first
                bits.append((byte >> i) & 1)

        # Length header (2 bytes, big-endian)
        length = len(data)
        length_bytes = length.to_bytes(2, byteorder='big')
        for byte in length_bytes:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

        # Payload
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)

        # Simple trailing pattern (optional)
        # Could add CRC, but omitted for brevity
        logger.debug(f"Encoded {len(data)} bytes into {len(bits)} bits")
        return bits

    def _modulate(self, bits: List[int]) -> Optional[List[complex]]:
        """
        Modulate bitstream into IQ samples based on modulation scheme.

        Args:
            bits: List of bits (0/1).

        Returns:
            List of complex IQ samples.
        """
        samples = []
        symbols_per_bit = 4  # Samples per symbol (oversampling)

        if self.modulation.upper() == "BPSK":
            for bit in bits:
                # BPSK: 0 -> +1, 1 -> -1
                symbol = 1.0 if bit == 0 else -1.0
                # Repeat for oversampling
                for _ in range(symbols_per_bit):
                    samples.append(complex(symbol, 0.0))

        elif self.modulation.upper() == "QPSK":
            # QPSK: group bits into dibits
            for i in range(0, len(bits) - (len(bits) % 2), 2):
                bit_pair = (bits[i], bits[i+1])
                # Map dibit to complex symbol
                if bit_pair == (0, 0):
                    symbol = complex(1, 1) / math.sqrt(2)
                elif bit_pair == (0, 1):
                    symbol = complex(1, -1) / math.sqrt(2)
                elif bit_pair == (1, 0):
                    symbol = complex(-1, 1) / math.sqrt(2)
                else:  # (1,1)
                    symbol = complex(-1, -1) / math.sqrt(2)
                for _ in range(symbols_per_bit):
                    samples.append(symbol)

        else:
            logger.error(f"Unsupported modulation: {self.modulation}")
            return None

        logger.debug(f"Modulated {len(bits)} bits into {len(samples)} IQ samples")
        return samples

    def _transmit(self, samples: List[complex], duration_sec: Optional[float] = None) -> bool:
        """
        Transmit IQ samples via hardware or simulate.

        Args:
            samples: List of complex IQ samples.
            duration_sec: Optional expected duration.

        Returns:
            True if transmission successful (or simulated).
        """
        if self.use_hardware and self._sdr is not None:
            # Placeholder for actual hardware transmission
            # self._sdr.transmit(samples)
            logger.error("Hardware transmission not implemented in this placeholder")
            return False
        else:
            # Simulate transmission: compute duration and log
            tx_time = len(samples) / self.sample_rate_hz
            if duration_sec is not None and abs(tx_time - duration_sec) > 0.01:
                logger.warning(f"Actual transmission time {tx_time:.3f}s differs from requested {duration_sec:.3f}s")
            logger.info(f"Simulated transmission of {len(samples)} samples ({tx_time:.3f} seconds)")
            # Optionally, write to a file for debugging
            # write_samples_to_file(samples, "tx_samples.iq")
            print(f"[SIM] Transmitting {len(samples)} samples at {self.sample_rate_hz} Hz...")
            return True

    def get_transmission_parameters(self) -> TransmissionParameters:
        """
        Return current transmission parameters.

        Returns:
            TransmissionParameters object.
        """
        return TransmissionParameters(
            frequency_hz=self.center_freq_hz,
            power_dbm=self.power_dbm,
            modulation=self.modulation,
            data_rate_bps=self.sample_rate_hz / 4  # oversampling factor = 4
        )


# Example usage (only executed when script is run directly)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tx = Sender(center_freq_hz=145.9e6, sample_rate_hz=2.4e6, power_dbm=30, modulation="BPSK")
    message = b"Hello, satellite!"
    success = tx.send(message)
    if success:
        print("Sent successfully")
    else:
        print("Transmission failed")