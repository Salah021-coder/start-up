# ============================================================================
# FILE: core/risk/signal_adapter.py
# Converts existing feature dictionaries to validated RiskSignals
# ============================================================================

from typing import Dict, Optional
from core.risk.risk_engine import RiskSignal
from core.risk.validator import SignalValidator
import logging

logger = logging.getLogger(__name__)


class FeatureToSignalAdapter:
    """
    Converts legacy feature dictionaries to validated RiskSignals
    
    This is the bridge between your old code and the new architecture.
    """
    
    def __init__(self):
        self.validator = SignalValidator()
    
    def convert_terrain_features(
        self,
        terrain: Dict
    ) -> Dict[str, RiskSignal]:
        """Convert terrain feature dict to signals"""
        
        signals = {}
        
        # Slope
        if 'slope_avg' in terrain:
            signal = self._create_signal(
                'slope_avg',
                terrain['slope_avg'],
                'degrees',
                terrain.get('data_quality', 'unknown')
            )
            if signal:
                signals['slope_avg'] = signal
        
        if 'slope_max' in terrain:
            signal = self._create_signal(
                'slope_max',
                terrain['slope_max'],
                'degrees',
                terrain.get('data_quality', 'unknown')
            )
            if signal:
                signals['slope_max'] = signal
        
        # Elevation
        if 'elevation_avg' in terrain:
            signal = self._create_signal(
                'elevation_avg',
                terrain['elevation_avg'],
                'meters',
                terrain.get('data_quality', 'unknown')
            )
            if signal:
                signals['elevation_avg'] = signal
        
        if 'elevation_min' in terrain:
            signal = self._create_signal(
                'elevation_min',
                terrain['elevation_min'],
                'meters',
                terrain.get('data_quality', 'unknown')
            )
            if signal:
                signals['elevation_min'] = signal
        
        if 'elevation_max' in terrain:
            signal = self._create_signal(
                'elevation_max',
                terrain['elevation_max'],
                'meters',
                terrain.get('data_quality', 'unknown')
            )
            if signal:
                signals['elevation_max'] = signal
        
        # Calculate elevation range if not present
        if 'elevation_min' in signals and 'elevation_max' in signals:
            range_val = signals['elevation_max'].value - signals['elevation_min'].value
            signals['elevation_range'] = RiskSignal(
                name='elevation_range',
                value=range_val,
                unit='meters',
                source='computed',
                confidence=min(signals['elevation_min'].confidence, signals['elevation_max'].confidence)
            )
        
        return signals
    
    def convert_environmental_features(
        self,
        environmental: Dict
    ) -> Dict[str, RiskSignal]:
        """Convert environmental feature dict to signals"""
        
        signals = {}
        
        # NDVI (vegetation)
        if 'ndvi_avg' in environmental:
            signal = self._create_signal(
                'ndvi_avg',
                environmental['ndvi_avg'],
                'index',
                environmental.get('data_quality', 'unknown')
            )
            if signal:
                signals['ndvi_avg'] = signal
        
        # Water occurrence
        if 'water_occurrence_avg' in environmental:
            signal = self._create_signal(
                'water_occurrence',
                environmental['water_occurrence_avg'],
                'percent',
                environmental.get('data_quality', 'unknown')
            )
            if signal:
                signals['water_occurrence'] = signal
        
        return signals
    
    def convert_all_features(
        self,
        features: Dict
    ) -> Dict[str, RiskSignal]:
        """
        Convert entire feature dict to signals
        
        Args:
            features: Dict with keys 'terrain', 'environmental', 'boundary'
            
        Returns:
            Dict of validated RiskSignals
        """
        all_signals = {}
        
        # Convert terrain
        if 'terrain' in features:
            terrain_signals = self.convert_terrain_features(features['terrain'])
            all_signals.update(terrain_signals)
            logger.info(f"Converted {len(terrain_signals)} terrain signals")
        else:
            logger.warning("No terrain features provided")
        
        # Convert environmental
        if 'environmental' in features:
            env_signals = self.convert_environmental_features(features['environmental'])
            all_signals.update(env_signals)
            logger.info(f"Converted {len(env_signals)} environmental signals")
        else:
            logger.warning("No environmental features provided")
        
        # Validate all signals
        valid_signals = self.validator.filter_valid_signals(all_signals)
        
        logger.info(
            f"Total signals: {len(all_signals)}, "
            f"Valid: {len(valid_signals)}, "
            f"Invalid: {len(all_signals) - len(valid_signals)}"
        )
        
        return valid_signals
    
    def extract_location(
        self,
        features: Dict
    ) -> Optional[Dict]:
        """Extract location from features"""
        
        boundary = features.get('boundary', {})
        centroid = boundary.get('centroid')
        
        if centroid and len(centroid) >= 2:
            return {
                'lon': centroid[0],
                'lat': centroid[1]
            }
        
        logger.warning("Could not extract location from features")
        return None
    
    def _create_signal(
        self,
        name: str,
        value: float,
        unit: str,
        source: str
    ) -> Optional[RiskSignal]:
        """Create signal with confidence based on source"""
        
        # Determine confidence from source
        confidence_map = {
            'gee': 0.95,
            'real_osm': 0.90,
            'enhanced': 0.85,
            'computed': 0.80,
            'estimated': 0.60,
            'mock': 0.50,
            'default': 0.30,
            'unknown': 0.50
        }
        
        confidence = confidence_map.get(source, 0.50)
        
        return self.validator.create_validated_signal(
            name=name,
            value=value,
            unit=unit,
            source=source,
            confidence=confidence
        )
