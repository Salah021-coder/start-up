# ============================================================================
# FILE: scripts/test_analysis.py
# Test Script for Complete Analysis Pipeline
# ============================================================================

"""
Test the complete analysis pipeline with a sample boundary

Usage:
    python scripts/test_analysis.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.analysis_processor import AnalysisProcessor
from core.boundary_manager import BoundaryManager
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def progress_callback(message: str, percent: int):
    """Progress callback"""
    print(f"[{percent:3d}%] {message}")


def test_analysis():
    """Test complete analysis pipeline"""
    
    print("\n" + "=" * 70)
    print("TESTING LAND ANALYSIS PIPELINE")
    print("=" * 70 + "\n")
    
    # Sample boundary (Sétif, Algeria)
    sample_coords = [
        [5.410, 36.190],
        [5.420, 36.190],
        [5.420, 36.200],
        [5.410, 36.200],
        [5.410, 36.190]
    ]
    
    try:
        # Step 1: Create boundary
        print("Step 1: Creating boundary...")
        boundary_manager = BoundaryManager()
        boundary_data = boundary_manager.create_from_coordinates(sample_coords)
        
        print(f"  ✓ Boundary created: {boundary_data['area_hectares']:.2f} ha")
        print(f"  ✓ Centroid: {boundary_data['centroid']}")
        
        # Step 2: Run analysis
        print("\nStep 2: Running analysis...")
        processor = AnalysisProcessor()
        
        results = processor.run_analysis(
            boundary_data=boundary_data,
            progress_callback=progress_callback
        )
        
        # Step 3: Display results
        print("\n" + "=" * 70)
        print("ANALYSIS RESULTS")
        print("=" * 70)
        
        print(f"\nAnalysis ID: {results['analysis_id']}")
        print(f"Overall Score: {results['overall_score']:.2f}/10")
        print(f"Confidence: {results['confidence_level']*100:.1f}%")
        
        print("\nTop 5 Recommendations:")
        for i, rec in enumerate(results['recommendations'][:5], 1):
            print(f"  {i}. {rec['usage_type']}: {rec['suitability_score']:.1f}/10")
        
        print("\nRisk Assessment:")
        risk = results['risk_assessment']
        print(f"  Overall Risk: {risk['overall_level'].title()}")
        print(f"  High Risks: {risk['high_risk_count']}")
        
        print("\nData Quality:")
        sources = results['data_sources']
        print(f"  Terrain: {sources['terrain']}")
        print(f"  Infrastructure: {sources['infrastructure']}")
        print(f"  Earth Engine: {'✓' if sources['earth_engine'] else '✗'}")
        
        # Step 4: Export results
        print("\n" + "=" * 70)
        print("EXPORTING RESULTS")
        print("=" * 70)
        
        output_dir = project_root / 'test_output'
        output_dir.mkdir(exist_ok=True)
        
        # Export JSON
        json_path = output_dir / 'test_results.json'
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"  ✓ JSON exported: {json_path}")
        
        # Export text report
        from utils.export_utils import ExportUtils
        
        text_report = ExportUtils.generate_text_report(results)
        report_path = output_dir / 'test_report.txt'
        with open(report_path, 'w') as f:
            f.write(text_report)
        print(f"  ✓ Text report exported: {report_path}")
        
        print("\n" + "=" * 70)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_analysis()
    sys.exit(0 if success else 1)
