# ============================================================================
# FILE: services/analysis_service.py
# Service Layer - Bridge between UI/API and Core
# ============================================================================

from typing import Dict, Optional, Callable
import logging

from core.orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig
from core.models.analysis_result import AnalysisResult

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Service layer for land analysis
    
    RESPONSIBILITIES:
    - Provides clean interface for UI/API
    - Handles session/request lifecycle
    - Manages errors gracefully for user consumption
    - Validates inputs at service boundary
    
    DOES NOT:
    - Compute anything (delegates to pipeline)
    - Store state (stateless service)
    - Make UI decisions
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize service
        
        Args:
            config: Pipeline configuration (optional)
        """
        self.config = config or PipelineConfig()
        self.pipeline = None
        logger.info("Analysis service initialized")
    
    def _ensure_pipeline(self):
        """Lazy-load pipeline on first use"""
        if self.pipeline is None:
            self.pipeline = AnalysisPipeline(self.config)
            logger.debug("Pipeline lazy-loaded")
    
    def analyze_land(
        self,
        boundary_data: Dict,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> tuple[Optional[AnalysisResult], Optional[str]]:
        """
        Run land analysis (main entry point)
        
        Args:
            boundary_data: Boundary geometry and metadata
            progress_callback: Optional progress callback
            
        Returns:
            (AnalysisResult, error_message)
            - On success: (result, None)
            - On failure: (None, user_friendly_error)
        """
        try:
            logger.info("Starting land analysis via service")
            
            # Validate inputs
            validation_error = self._validate_inputs(boundary_data)
            if validation_error:
                logger.error(f"Input validation failed: {validation_error}")
                return None, validation_error
            
            # Ensure pipeline is loaded
            self._ensure_pipeline()
            
            # Run analysis
            result = self.pipeline.run_analysis(
                boundary_data=boundary_data,
                progress_callback=progress_callback
            )
            
            # Validate result
            if not result.is_valid():
                errors = result.validate()
                logger.error(f"Result validation failed: {errors}")
                return None, f"Analysis produced invalid results: {'; '.join(errors)}"
            
            logger.info(
                f"Analysis completed successfully: {result.analysis_id}, "
                f"score={result.overall_score:.1f}/10"
            )
            
            return result, None
            
        except ValueError as e:
            # Input validation errors - user's fault
            error_msg = self._format_user_error(e)
            logger.warning(f"User input error: {error_msg}")
            return None, error_msg
        
        except RuntimeError as e:
            # System errors - our fault
            error_msg = self._format_system_error(e)
            logger.error(f"System error during analysis: {e}", exc_info=True)
            return None, error_msg
        
        except Exception as e:
            # Unexpected errors
            error_msg = self._format_unexpected_error(e)
            logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            return None, error_msg
    
    def _validate_inputs(self, boundary_data: Dict) -> Optional[str]:
        """
        Validate inputs at service boundary
        
        Returns:
            Error message if invalid, None if valid
        """
        if not boundary_data:
            return "No boundary data provided"
        
        if 'geometry' not in boundary_data:
            return "Boundary data missing 'geometry' field"
        
        if 'area_m2' not in boundary_data:
            return "Boundary data missing 'area_m2' field"
        
        area_km2 = boundary_data['area_m2'] / 1_000_000
        
        if area_km2 > self.config.max_area_km2:
            return (
                f"Area too large: {area_km2:.2f} km². "
                f"Maximum allowed: {self.config.max_area_km2} km²"
            )
        
        if boundary_data['area_m2'] < 100:
            return f"Area too small: {boundary_data['area_m2']:.0f} m². Minimum: 100 m²"
        
        return None
    
    def _format_user_error(self, error: Exception) -> str:
        """Format user-facing error message for input errors"""
        error_str = str(error)
        
        # Make it user-friendly
        if "area too large" in error_str.lower():
            return f"❌ {error_str}\n\nPlease draw a smaller boundary."
        
        if "area too small" in error_str.lower():
            return f"❌ {error_str}\n\nPlease draw a larger boundary."
        
        if "missing" in error_str.lower():
            return f"❌ Invalid boundary data: {error_str}"
        
        return f"❌ Input Error: {error_str}"
    
    def _format_system_error(self, error: Exception) -> str:
        """Format user-facing error for system errors"""
        error_str = str(error)
        
        if "earth engine" in error_str.lower() or "gee" in error_str.lower():
            return """
❌ **Earth Engine Not Available**

The analysis requires Google Earth Engine for terrain data.

**Solutions:**
1. Configure GEE credentials in settings
2. Or run `earthengine authenticate` locally
3. Contact support if issue persists

**Technical Details:** {error}
""".format(error=error_str)
        
        if "terrain" in error_str.lower():
            return f"""
❌ **Terrain Data Extraction Failed**

Could not extract terrain information for this location.

**Possible Causes:**
- Earth Engine timeout (try again)
- Location outside data coverage
- Temporary service interruption

**Technical Details:** {error_str}
"""
        
        if "infrastructure" in error_str.lower():
            return f"""
❌ **Infrastructure Data Extraction Failed**

Could not fetch infrastructure information.

**Possible Causes:**
- OpenStreetMap timeout (try again)
- Network connectivity issues
- Location outside coverage area

**Technical Details:** {error_str}
"""
        
        return f"""
❌ **Analysis Failed**

An error occurred during the analysis process.

**What to do:**
1. Try running the analysis again
2. If problem persists, try a different location
3. Contact support with the analysis ID

**Technical Details:** {error_str}
"""
    
    def _format_unexpected_error(self, error: Exception) -> str:
        """Format user-facing error for unexpected errors"""
        return f"""
❌ **Unexpected Error**

An unexpected error occurred during analysis.

**What to do:**
1. Try again
2. If problem persists, contact support
3. Check system logs for details

**Error Type:** {type(error).__name__}
**Details:** {str(error)}
"""
    
    # ========== ADDITIONAL HELPERS ==========
    
    def get_service_status(self) -> Dict:
        """
        Get service health status
        
        Useful for API health checks
        """
        status = {
            'service': 'analysis_service',
            'status': 'unknown',
            'components': {}
        }
        
        try:
            # Check if we can create a pipeline
            self._ensure_pipeline()
            
            status['components']['pipeline'] = 'ok'
            status['components']['earth_engine'] = (
                'available' if self.pipeline.ee_available else 'unavailable'
            )
            status['components']['osm'] = (
                'real' if self.config.use_real_osm else 'mock'
            )
            status['components']['ml'] = (
                'enabled' if self.config.enable_ml_predictions else 'disabled'
            )
            
            # Overall status
            if self.pipeline.ee_available:
                status['status'] = 'healthy'
            else:
                status['status'] = 'degraded'
            
        except Exception as e:
            logger.error(f"Service status check failed: {e}")
            status['status'] = 'unhealthy'
            status['error'] = str(e)
        
        return status
    
    def validate_boundary_only(self, boundary_data: Dict) -> tuple[bool, Optional[str]]:
        """
        Validate boundary without running analysis
        
        Returns:
            (is_valid, error_message)
        """
        error = self._validate_inputs(boundary_data)
        
        if error:
            return False, error
        
        return True, None
    
    def estimate_analysis_time(self, boundary_data: Dict) -> Dict:
        """
        Estimate analysis time
        
        Returns:
            Dict with time estimates
        """
        area_km2 = boundary_data.get('area_m2', 0) / 1_000_000
        
        # Base time estimates (rough)
        base_time = 10  # seconds
        
        # Larger areas take longer
        area_factor = 1 + (area_km2 / 10)
        
        # EE vs no-EE
        ee_factor = 1.5 if self.pipeline and self.pipeline.ee_available else 1.0
        
        # OSM factor
        osm_factor = 1.2 if self.config.use_real_osm else 1.0
        
        estimated_seconds = base_time * area_factor * ee_factor * osm_factor
        
        return {
            'estimated_seconds': int(estimated_seconds),
            'estimated_range': f"{int(estimated_seconds * 0.7)}-{int(estimated_seconds * 1.3)} seconds",
            'factors': {
                'area_km2': area_km2,
                'earth_engine': self.pipeline.ee_available if self.pipeline else False,
                'real_osm': self.config.use_real_osm
            }
        }


# ============================================================================
# Singleton instance for Streamlit (optional)
# ============================================================================

_service_instance = None


def get_analysis_service(config: Optional[PipelineConfig] = None) -> AnalysisService:
    """
    Get singleton service instance
    
    Useful for Streamlit to avoid re-creating pipeline
    """
    global _service_instance
    
    if _service_instance is None:
        _service_instance = AnalysisService(config)
        logger.info("Created singleton analysis service")
    
    return _service_instance


def reset_analysis_service():
    """Reset singleton (for testing)"""
    global _service_instance
    _service_instance = None
    logger.info("Reset analysis service singleton")
