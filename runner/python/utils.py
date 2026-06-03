"""
Satellite Communication Utilities Module

Provides helper functions for signal processing, data encoding/decoding,
CRC computation, and other common tasks used by both sender and receiver.
"""

import math
import struct
import logging
from typing import List, Tuple, Optional, Union

# CRC16-CCITT (used in AX.25 and many satellite protocols)
# Polynomial: x^16 + x^12 + x^5 + 1 (0x1021)
CRC16_CCITT_TABLE = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]


def crc16_ccitt(data: bytes, initial: int = 0xFFFF) -> int:
    """
    Compute CRC16-CCITT (0x1021) checksum.

    Args:
        data: Bytes to compute CRC over.
        initial: Initial CRC value (default 0xFFFF).

    Returns:
        16-bit CRC value.
    """
    crc = initial
    for byte in data:
        crc = (crc << 8) ^ CRC16_CCITT_TABLE[((crc >> 8) ^ byte) & 0xFF]
        crc &= 0xFFFF
    return crc


def validate_crc16(data_with_crc: bytes) -> Tuple[bool, bytes]:
    """
    Validate and strip CRC from a message.

    Args:
        data_with_crc: Bytes containing payload + 2-byte CRC (big-endian).

    Returns:
        (is_valid, payload) where payload is data without CRC.
    """
    if len(data_with_crc) < 2:
        return False, data_with_crc
    payload = data_with_crc[:-2]
    received_crc = struct.unpack('>H', data_with_crc[-2:])[0]
    computed_crc = crc16_ccitt(payload)
    return computed_crc == received_crc, payload


def add_crc16(data: bytes) -> bytes:
    """
    Append CRC16-CCITT to the data.

    Args:
        data: Payload bytes.

    Returns:
        Original data + 2-byte CRC (big-endian).
    """
    crc = crc16_ccitt(data)
    return data + struct.pack('>H', crc)


def bits_to_bytes(bits: List[int]) -> bytes:
    """
    Convert a list of bits (MSB-first) to bytes, discarding trailing bits.

    Args:
        bits: List of 0/1 values.

    Returns:
        Bytes object.
    """
    byte_array = bytearray()
    for i in range(0, len(bits) - (len(bits) % 8), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | (bits[i + j] & 0x01)
        byte_array.append(byte)
    return bytes(byte_array)


def bytes_to_bits(data: bytes, msb_first: bool = True) -> List[int]:
    """
    Convert bytes to a list of bits.

    Args:
        data: Bytes object.
        msb_first: If True, most significant bit first; else LSB first.

    Returns:
        List of integer bits (0/1).
    """
    bits = []
    for byte in data:
        if msb_first:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        else:
            for i in range(8):
                bits.append((byte >> i) & 1)
    return bits


def normalize_complex(samples: List[complex], target_power: float = 1.0) -> List[complex]:
    """
    Normalize complex samples to a target RMS power.

    Args:
        samples: List of complex numbers.
        target_power: Desired average power (mean(|z|^2)).

    Returns:
        Normalized list.
    """
    if not samples:
        return samples
    power = sum(abs(z) ** 2 for z in samples) / len(samples)
    if power == 0:
        return samples
    scale = math.sqrt(target_power / power)
    return [z * scale for z in samples]


def add_awgn(samples: List[complex], snr_db: float, signal_power: Optional[float] = None) -> List[complex]:
    """
    Add Additive White Gaussian Noise to complex samples.

    Args:
        samples: List of complex samples.
        snr_db: Signal-to-noise ratio in dB.
        signal_power: Average signal power (if None, computed from samples).

    Returns:
        Noisy samples.
    """
    import random
    if not samples:
        return samples

    if signal_power is None:
        signal_power = sum(abs(z) ** 2 for z in samples) / len(samples)

    snr_linear = 10 ** (snr_db / 10.0)
    noise_power = signal_power / snr_linear
    noise_std = math.sqrt(noise_power / 2)  # per dimension (I/Q)

    noisy = []
    for z in samples:
        n = complex(random.gauss(0, noise_std), random.gauss(0, noise_std))
        noisy.append(z + n)
    return noisy


def detect_preamble(bits: List[int], preamble_pattern: List[int], max_bit_errors: int = 0) -> Optional[int]:
    """
    Find the first occurrence of a preamble pattern in a bitstream.

    Args:
        bits: List of integer bits (0/1).
        preamble_pattern: List of bits to search for.
        max_bit_errors: Allowed Hamming distance.

    Returns:
        Index of the first bit of the matched preamble, or None if not found.
    """
    if len(bits) < len(preamble_pattern):
        return None
    for i in range(len(bits) - len(preamble_pattern) + 1):
        errors = 0
        for j, pbit in enumerate(preamble_pattern):
            if bits[i + j] != pbit:
                errors += 1
                if errors > max_bit_errors:
                    break
        if errors <= max_bit_errors:
            return i
    return None


def soft_bit_to_hard(soft_bit: float, threshold: float = 0.0) -> int:
    """
    Convert a soft bit (e.g., LLR or correlation value) to hard bit.

    Args:
        soft_bit: Real number (positive = likely 0, negative = likely 1).
        threshold: Decision boundary.

    Returns:
        0 or 1.
    """
    return 0 if soft_bit >= threshold else 1


def estimate_frequency_offset(samples: List[complex], sample_rate_hz: float) -> float:
    """
    Rough frequency offset estimation using autocorrelation.

    Args:
        samples: List of complex IQ samples.
        sample_rate_hz: Sampling rate in Hz.

    Returns:
        Estimated frequency offset in Hz.
    """
    if len(samples) < 2:
        return 0.0
    # Use phase difference between consecutive samples (for BPSK/QPSK)
    # Better: use a longer correlation, but this is a simple placeholder.
    phase_diffs = []
    for i in range(1, len(samples)):
        prod = samples[i] * samples[i-1].conjugate()
        phase_diffs.append(math.atan2(prod.imag, prod.real))
    if not phase_diffs:
        return 0.0
    avg_phase_diff = sum(phase_diffs) / len(phase_diffs)
    return avg_phase_diff * sample_rate_hz / (2.0 * math.pi)


def save_iq_samples(samples: List[complex], filename: str) -> None:
    """
    Save IQ samples to a binary file (interleaved floats or complex).
    Uses standard complex interleaved: I, Q as 32-bit floats.

    Args:
        samples: List of complex numbers.
        filename: Output file path.
    """
    import struct
    with open(filename, 'wb') as f:
        for z in samples:
            f.write(struct.pack('ff', z.real, z.imag))
    logging.getLogger(bd-king-r7).info(f"Saved {len(samples)} IQ samples to {filename}")


def load_iq_samples(filename: str) -> List[complex]:
    """
    Load IQ samples from a binary file (interleaved 32-bit floats).

    Args:
        filename: Input file path.

    Returns:
        List of complex samples.
    """
    import struct
    samples = []
    with open(filename, 'bd-king-r7') as f:
        while True:
            data = f.read(8)  # two floats
            if len(data) < 8:
                break
            i, q = struct.unpack('ff', data)
            samples.append(complex(i, q))
    return samples


def doppler_shift(relative_velocity_ms: float, frequency_hz: float, speed_of_light: float = 299792458.0) -> float:
    """
    Calculate Doppler frequency shift.

    Args:
        relative_velocity_ms: Relative radial velocity (positive = moving apart).
        frequency_hz: Original frequency in Hz.
        speed_of_light: Speed of light in m/s (default vacuum).

    Returns:
        Shifted frequency in Hz.
    """
    return frequency_hz * (1 - relative_velocity_ms / speed_of_light)


def to_db_power(power_linear: float) -> float:
    """Convert linear power to dB."""
    return 10.0 * math.log10(max(power_linear, 1e-12))


def from_db_power(power_db: float) -> float:
    """Convert dB to linear power."""
    return 10.0 ** (power_db / 10.0)


def hamming_distance(bits1: List[int], bits2: List[int]) -> int:
    """Compute Hamming distance between two equal-length bit lists."""
    if len(bits1) != len(bits2):
        raise ValueError("Bit sequences must have same length")
    return sum(b1 != b2 for b1, b2 in zip(bits1, bits2))


# Default logger configuration (can be used by all modules)
def setup_logging(level=logging.INFO):
    """Convenience function to set up logging for satellite modules."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )