# ============================================================================
# FILE: utils/export_utils.py
# Export Utilities for Analysis Results
# ============================================================================

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ExportUtils:
    """Utilities for exporting analysis results"""
    
    @staticmethod
    def export_to_json(
        results: Dict,
        output_path: str,
        pretty: bool = True
    ) -> bool:
        """
        Export results to JSON file
        
        Args:
            results: Analysis results dictionary
            output_path: Output file path
            pretty: Use indentation
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w') as f:
                if pretty:
                    json.dump(results, f, indent=2, default=str)
                else:
                    json.dump(results, f, default=str)
            
            logger.info(f"Results exported to JSON: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return False
    
    @staticmethod
    def export_to_csv(
        results: Dict,
        output_path: str
    ) -> bool:
        """
        Export results to CSV file (summary)
        
        Args:
            results: Analysis results dictionary
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            # Extract summary data
            rows = []
            
            # Overall metrics
            rows.append(['Metric', 'Value'])
            rows.append(['Analysis ID', results.get('analysis_id', '')])
            rows.append(['Date', results.get('timestamp', '')])
            rows.append(['Overall Score', results.get('overall_score', 0)])
            rows.append(['Confidence', results.get('confidence_level', 0)])
            rows.append([''])
            
            # Boundary info
            boundary = results.get('boundary', {})
            rows.append(['Area (hectares)', boundary.get('area_hectares', 0)])
            rows.append(['Area (acres)', boundary.get('area_acres', 0)])
            rows.append([''])
            
            # Top recommendations
            rows.append(['Top Recommendations', ''])
            recommendations = results.get('recommendations', [])
            for i, rec in enumerate(recommendations[:5], 1):
                rows.append([
                    f"{i}. {rec.get('usage_type', '')}",
                    f"{rec.get('suitability_score', 0):.1f}/10"
                ])
            
            # Write CSV
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            logger.info(f"Results exported to CSV: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False
    
    @staticmethod
    def export_recommendations_csv(
        recommendations: List[Dict],
        output_path: str
    ) -> bool:
        """
        Export recommendations to detailed CSV
        
        Args:
            recommendations: List of recommendation dicts
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Rank',
                    'Land Use Type',
                    'Suitability Score',
                    'Confidence',
                    'Supporting Factors',
                    'Concerns'
                ])
                
                # Rows
                for rec in recommendations:
                    writer.writerow([
                        rec.get('rank', ''),
                        rec.get('usage_type', ''),
                        rec.get('suitability_score', 0),
                        rec.get('confidence', 0),
                        '; '.join(rec.get('supporting_factors', [])),
                        '; '.join(rec.get('concerns', []))
                    ])
            
            logger.info(f"Recommendations exported to CSV: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Recommendations CSV export failed: {e}")
            return False
    
    @staticmethod
    def export_geojson(
        boundary: Dict,
        output_path: str,
        properties: Dict = None
    ) -> bool:
        """
        Export boundary to GeoJSON
        
        Args:
            boundary: Boundary dictionary with geometry
            output_path: Output file path
            properties: Additional properties to include
            
        Returns:
            True if successful
        """
        try:
            geojson = boundary.get('geojson', {})
            
            if properties:
                if 'properties' not in geojson:
                    geojson['properties'] = {}
                geojson['properties'].update(properties)
            
            with open(output_path, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            logger.info(f"Boundary exported to GeoJSON: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"GeoJSON export failed: {e}")
            return False
    
    @staticmethod
    def generate_text_report(results: Dict) -> str:
        """
        Generate text summary report
        
        Args:
            results: Analysis results
            
        Returns:
            Formatted text report
        """
        lines = []
        
        lines.append("=" * 70)
        lines.append("LAND ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Header
        lines.append(f"Analysis ID: {results.get('analysis_id', 'N/A')}")
        lines.append(f"Date: {results.get('timestamp', 'N/A')}")
        lines.append("")
        
        # Location
        boundary = results.get('boundary', {})
        centroid = boundary.get('centroid', [0, 0])
        lines.append("LOCATION")
        lines.append("-" * 70)
        lines.append(f"  Coordinates: {centroid[1]:.4f}°N, {centroid[0]:.4f}°E")
        lines.append(f"  Area: {boundary.get('area_hectares', 0):.2f} hectares ({boundary.get('area_acres', 0):.2f} acres)")
        lines.append("")
        
        # Overall Assessment
        lines.append("OVERALL ASSESSMENT")
        lines.append("-" * 70)
        lines.append(f"  Suitability Score: {results.get('overall_score', 0):.1f}/10")
        lines.append(f"  Confidence: {results.get('confidence_level', 0)*100:.0f}%")
        
        risk = results.get('risk_assessment', {})
        lines.append(f"  Overall Risk: {risk.get('overall_level', 'Unknown').title()}")
        lines.append("")
        
        # Top Recommendations
        lines.append("TOP RECOMMENDATIONS")
        lines.append("-" * 70)
        recommendations = results.get('recommendations', [])
        for i, rec in enumerate(recommendations[:5], 1):
            lines.append(f"  {i}. {rec.get('usage_type', 'Unknown')}")
            lines.append(f"     Score: {rec.get('suitability_score', 0):.1f}/10")
            
            factors = rec.get('supporting_factors', [])
            if factors:
                lines.append(f"     Strengths: {factors[0]}")
        lines.append("")
        
        # Key Insights
        insights = results.get('key_insights', {})
        if insights:
            lines.append("KEY INSIGHTS")
            lines.append("-" * 70)
            
            strengths = insights.get('strengths', [])
            if strengths:
                lines.append("  Strengths:")
                for strength in strengths[:3]:
                    lines.append(f"    • {strength}")
            
            concerns = insights.get('concerns', [])
            if concerns:
                lines.append("  Concerns:")
                for concern in concerns[:3]:
                    lines.append(f"    • {concern}")
            lines.append("")
        
        # Data Quality
        sources = results.get('data_sources', {})
        lines.append("DATA QUALITY")
        lines.append("-" * 70)
        lines.append(f"  Terrain: {sources.get('terrain', 'unknown')}")
        lines.append(f"  Infrastructure: {sources.get('infrastructure', 'unknown')}")
        lines.append(f"  Earth Engine: {'Available' if sources.get('earth_engine') else 'Not Available'}")
        lines.append("")
        
        lines.append("=" * 70)
        lines.append("End of Report")
        lines.append("=" * 70)
        
        return "\n".join(lines)
