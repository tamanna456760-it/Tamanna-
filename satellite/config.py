"""
Satellite Communication Configuration Module

This module centralizes configuration parameters for both the sender and receiver,
including hardware settings, modulation parameters, frequency bands, and data framing.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import logging

# Default logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class FrequencyBand:
    """Represents an amateur or satellite frequency band."""
    name: str
    uplink_lower_hz: float
    uplink_upper_hz: float
    downlink_lower_hz: float
    downlink_upper_hz: float


# Common satellite frequency bands (simplified)
VHF_BAND = FrequencyBand(
    name="VHF",
    uplink_lower_hz=144.0e6,
    uplink_upper_hz=146.0e6,
    downlink_lower_hz=145.8e6,
    downlink_upper_hz=146.0e6
)

UHF_BAND = FrequencyBand(
    name="UHF",
    uplink_lower_hz=430.0e6,
    uplink_upper_hz=440.0e6,
    downlink_lower_hz=435.0e6,
    downlink_upper_hz=438.0e6
)

L_BAND = FrequencyBand(
    name="L-Band",
    uplink_lower_hz=1.26e9,
    uplink_upper_hz=1.27e9,
    downlink_lower_hz=1.52e9,
    downlink_upper_hz=1.56e9
)

S_BAND = FrequencyBand(
    name="S-Band",
    uplink_lower_hz=2.025e9,
    uplink_upper_hz=2.110e9,
    downlink_lower_hz=2.200e9,
    downlink_upper_hz=2.300e9
)


@dataclass
class ModulationConfig:
    """Configuration for a modulation scheme."""
    name: str
    bits_per_symbol: int
    oversampling_factor: int = 4  # samples per symbol


# Supported modulation schemes
MODULATION_BPSK = ModulationConfig("BPSK", bits_per_symbol=1, oversampling_factor=4)
MODULATION_QPSK = ModulationConfig("QPSK", bits_per_symbol=2, oversampling_factor=4)
MODULATION_8PSK = ModulationConfig("8PSK", bits_per_symbol=3, oversampling_factor=6)
MODULATION_GMSK = ModulationConfig("GMSK", bits_per_symbol=1, oversampling_factor=5)

# Select default modulation
DEFAULT_MODULATION = MODULATION_BPSK


@dataclass
class FrameConfig:
    """Framing and encoding configuration."""
    preamble_bytes: bytes = b'\xAA\xBB'      # frame start marker
    use_crc16: bool = True
    use_fec: bool = False                    # forward error correction
    max_payload_bytes: int = 256
    length_field_size_bytes: int = 2
    tail_bits: int = 0                       # number of trailing bits


DEFAULT_FRAME_CONFIG = FrameConfig()


@dataclass
class HardwareConfig:
    """Hardware-specific configuration (SDR, antenna, etc.)."""
    device_type: str = "simulated"   # "rtlsdr", "hackrf", "plutosdr", "simulated"
    sample_rate_hz: float = 2.4e6
    center_freq_hz: float = 145.9e6    # default VHF downlink
    gain_db: float = 20.0
    antenna: Optional[str] = None
    bias_tee: bool = False
    ppm_error: float = 0.0             # oscillator correction in parts per million


@dataclass
class SatelliteConfig:
    """High-level satellite communication configuration."""
    name: str = "GenericSat"
    norad_id: Optional[int] = None
    frequency_band: FrequencyBand = VHF_BAND
    modulation: ModulationConfig = DEFAULT_MODULATION
    frame: FrameConfig = field(default_factory=FrameConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    downlink_freq_hz: Optional[float] = None
    uplink_freq_hz: Optional[float] = None

    def __post_init__(self):
        """Set default uplink/downlink frequencies based on band if not provided."""
        if self.downlink_freq_hz is None:
            self.downlink_freq_hz = (self.frequency_band.downlink_lower_hz +
                                     self.frequency_band.downlink_upper_hz) / 2
        if self.uplink_freq_hz is None:
            self.uplink_freq_hz = (self.frequency_band.uplink_lower_hz +
                                   self.frequency_band.uplink_upper_hz) / 2


# Predefined satellite configurations for common satellites
CONFIG_SAT_NOAA = SatelliteConfig(
    name="NOAA-15",
    norad_id=25338,
    frequency_band=VHF_BAND,
    downlink_freq_hz=137.62e6,
    modulation=MODULATION_GMSK  # APT uses AM, but placeholder
)

CONFIG_SAT_ISS = SatelliteConfig(
    name="ISS",
    norad_id=25544,
    frequency_band=VHF_BAND,
    downlink_freq_hz=145.8e6,
    uplink_freq_hz=144.49e6,
    modulation=MODULATION_BPSK
)

CONFIG_SAT_ESHAIL = SatelliteConfig(
    name="Es'hail-2",
    norad_id=43700,
    frequency_band=S_BAND,
    downlink_freq_hz=2.400e9,
    uplink_freq_hz=2.400e9,
    modulation=MODULATION_QPSK
)


def get_config(satellite_name: str = "Generic") -> SatelliteConfig:
    """
    Retrieve a predefined configuration for a known satellite.

    Args:
        satellite_name: Name of the satellite (case-insensitive).

    Returns:
        SatelliteConfig object. If not found, returns default generic config.
    """
    configs = {
        "noaa": CONFIG_SAT_NOAA,
        "iss": CONFIG_SAT_ISS,
        "eshail": CONFIG_SAT_ESHAIL,
        "eshail-2": CONFIG_SAT_ESHAIL
    }
    sat = configs.get(satellite_name.lower())
    if sat is None:
        logging.getLogger(__name__).warning(f"Unknown satellite '{satellite_name}', using generic config")
        return SatelliteConfig()
    return sat


# Global configuration object for the whole system (optional)
GLOBAL_CONFIG = SatelliteConfig()


def reload_config(new_config: SatelliteConfig) -> None:
    """Replace the global configuration."""
    global GLOBAL_CONFIG
    GLOBAL_CONFIG = new_config
    logging.getLogger(__name__).info("Global configuration reloaded")


# Helper to produce a hardware-friendly dictionary for SDR backends
def to_sdr_dict(config: HardwareConfig) -> Dict[str, Any]:
    """
    Convert hardware config to a dictionary suitable for SDR driver initialization.

    Args:
        config: HardwareConfig object.

    Returns:
        Dictionary with keys: sample_rate, center_freq, gain, ppm_error, etc.
    """
    return {
        "sample_rate_hz": config.sample_rate_hz,
        "center_freq_hz": config.center_freq_hz,
        "gain_db": config.gain_db,
        "bias_tee": config.bias_tee,
        "ppm_error": config.ppm_error,
        "device_type": config.device_type,
        "antenna": config.antenna
    }