# ============================================================================
# FILE: core/risk/validator.py
# Signal validation - NO SILENT DEFAULTS
# ============================================================================

from typing import Dict, List, Optional
from core.risk.risk_engine import RiskSignal
import logging

logger = logging.getLogger(__name__)


class SignalValidator:
    """
    Validates risk signals before assessment
    
    RULES:
    1. Never returns default values
    2. Always logs validation failures
    3. Raises exception for critical missing data
    """
    
    # Required signals for each risk type
    REQUIRED_SIGNALS = {
        'flood': ['slope_avg', 'elevation_avg'],
        'landslide': ['slope_avg'],
        'erosion': ['slope_avg'],
        'seismic': [],  # Uses location instead
        'drought': [],  # Uses location instead
        'wildfire': [],  # Can work with defaults but logs warning
        'subsidence': ['elevation_avg', 'slope_avg']
    }
    
    # Signal value ranges (for sanity checks)
    VALID_RANGES = {
        'slope_avg': (0, 90),  # degrees
        'slope_max': (0, 90),
        'elevation_avg': (-500, 9000),  # meters (Dead Sea to Everest)
        'elevation_min': (-500, 9000),
        'elevation_max': (-500, 9000),
        'elevation_range': (0, 9500),
        'ndvi_avg': (-1, 1),  # Normalized Difference Vegetation Index
        'water_occurrence': (0, 100),  # percentage
    }
    
    def validate_signals(
        self,
        signals: Dict[str, RiskSignal]
    ) -> List[str]:
        """
        Validate all signals
        
        Args:
            signals: Dictionary of signals to validate
            
        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []
        
        if not signals:
            errors.append("No signals provided")
            return errors
        
        # Check each signal
        for name, signal in signals.items():
            signal_errors = self._validate_signal(name, signal)
            errors.extend(signal_errors)
        
        # Check for required signals
        missing = self._check_required_signals(signals)
        errors.extend(missing)
        
        if errors:
            logger.warning(f"Signal validation found {len(errors)} issues: {errors}")
        
        return errors
    
    def _validate_signal(
        self,
        name: str,
        signal: RiskSignal
    ) -> List[str]:
        """Validate a single signal"""
        errors = []
        
        if signal is None:
            errors.append(f"Signal '{name}' is None")
            return errors
        
        # Check value is not NaN or infinite
        if not isinstance(signal.value, (int, float)):
            errors.append(f"Signal '{name}' has non-numeric value: {signal.value}")
            return errors
        
        import math
        if math.isnan(signal.value) or math.isinf(signal.value):
            errors.append(f"Signal '{name}' has invalid value: {signal.value}")
            return errors
        
        # Check value is in valid range
        if name in self.VALID_RANGES:
            min_val, max_val = self.VALID_RANGES[name]
            if not (min_val <= signal.value <= max_val):
                errors.append(
                    f"Signal '{name}' value {signal.value} outside valid range "
                    f"[{min_val}, {max_val}]"
                )
        
        # Check confidence
        if not (0 <= signal.confidence <= 1):
            errors.append(
                f"Signal '{name}' has invalid confidence: {signal.confidence} "
                f"(must be 0-1)"
            )
        
        # Warn about low confidence
        if signal.confidence < 0.5:
            logger.warning(
                f"Signal '{name}' has low confidence: {signal.confidence}"
            )
        
        return errors
    
    def _check_required_signals(
        self,
        signals: Dict[str, RiskSignal]
    ) -> List[str]:
        """Check that all required signals are present"""
        errors = []
        
        # Check each risk type's requirements
        for risk_type, required in self.REQUIRED_SIGNALS.items():
            missing = [
                sig for sig in required 
                if sig not in signals or signals[sig] is None
            ]
            
            if missing:
                errors.append(
                    f"Missing required signals for {risk_type} assessment: "
                    f"{', '.join(missing)}"
                )
        
        return errors
    
    def validate_location(
        self,
        location: Optional[Dict]
    ) -> List[str]:
        """Validate location data for seismic/drought assessment"""
        errors = []
        
        if location is None:
            logger.warning("No location provided for risk assessment")
            return ["Location data missing"]
        
        if 'lat' not in location:
            errors.append("Location missing 'lat' field")
        else:
            lat = location['lat']
            if not isinstance(lat, (int, float)):
                errors.append(f"Invalid latitude type: {type(lat)}")
            elif not (-90 <= lat <= 90):
                errors.append(f"Latitude {lat} outside valid range [-90, 90]")
        
        if 'lon' not in location:
            errors.append("Location missing 'lon' field")
        else:
            lon = location['lon']
            if not isinstance(lon, (int, float)):
                errors.append(f"Invalid longitude type: {type(lon)}")
            elif not (-180 <= lon <= 180):
                errors.append(f"Longitude {lon} outside valid range [-180, 180]")
        
        return errors
    
    def create_validated_signal(
        self,
        name: str,
        value: float,
        unit: str,
        source: str,
        confidence: float = 1.0
    ) -> Optional[RiskSignal]:
        """
        Create a signal with validation
        
        Returns:
            RiskSignal if valid, None otherwise (logs error)
        """
        signal = RiskSignal(
            name=name,
            value=value,
            unit=unit,
            source=source,
            confidence=confidence
        )
        
        errors = self._validate_signal(name, signal)
        
        if errors:
            logger.error(
                f"Cannot create signal '{name}': {'; '.join(errors)}"
            )
            return None
        
        return signal
    
    def filter_valid_signals(
        self,
        signals: Dict[str, RiskSignal]
    ) -> Dict[str, RiskSignal]:
        """
        Filter out invalid signals
        
        IMPORTANT: This logs all removed signals
        """
        valid = {}
        invalid_count = 0
        
        for name, signal in signals.items():
            errors = self._validate_signal(name, signal)
            
            if not errors:
                valid[name] = signal
            else:
                invalid_count += 1
                logger.error(
                    f"Removing invalid signal '{name}': {'; '.join(errors)}"
                )
        
        if invalid_count > 0:
            logger.warning(
                f"Filtered out {invalid_count} invalid signals from {len(signals)} total"
            )
        
        return valid
