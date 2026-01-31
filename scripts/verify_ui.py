# ============================================================================
# FILE: scripts/verify_ui.py
# Verify UI Files and Structure
# ============================================================================

"""
Verify that all UI files exist and can be imported

Usage:
    python scripts/verify_ui.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def verify_ui_structure():
    """Verify UI file structure"""
    
    print("=" * 70)
    print("VERIFYING UI STRUCTURE")
    print("=" * 70 + "\n")
    
    # Check directories
    ui_dir = project_root / 'ui'
    pages_dir = ui_dir / 'pages'
    components_dir = ui_dir / 'components'
    
    print("Checking directories...")
    if ui_dir.exists():
        print(f"  ✓ {ui_dir}")
    else:
        print(f"  ✗ {ui_dir} - NOT FOUND")
        return False
    
    if pages_dir.exists():
        print(f"  ✓ {pages_dir}")
    else:
        print(f"  ✗ {pages_dir} - NOT FOUND")
        return False
    
    if components_dir.exists():
        print(f"  ✓ {components_dir}")
    else:
        print(f"  ✗ {components_dir} - NOT FOUND")
        return False
    
    print()
    
    # Check required page files
    required_pages = [
        'home.py',
        'analysis.py',
        'results.py',
        'history.py',
        'risk_analysis.py',
        'heatmap.py'
    ]
    
    print("Checking page files...")
    missing_pages = []
    for page in required_pages:
        page_path = pages_dir / page
        if page_path.exists():
            print(f"  ✓ {page}")
        else:
            print(f"  ✗ {page} - NOT FOUND")
            missing_pages.append(page)
    
    print()
    
    # Try to import pages
    print("Testing imports...")
    import_errors = []
    
    try:
        from ui.pages import home
        print("  ✓ home")
    except Exception as e:
        print(f"  ✗ home - {e}")
        import_errors.append(('home', e))
    
    try:
        from ui.pages import analysis
        print("  ✓ analysis")
    except Exception as e:
        print(f"  ✗ analysis - {e}")
        import_errors.append(('analysis', e))
    
    try:
        from ui.pages import results
        print("  ✓ results")
    except Exception as e:
        print(f"  ✗ results - {e}")
        import_errors.append(('results', e))
    
    try:
        from ui.pages import history
        print("  ✓ history")
    except Exception as e:
        print(f"  ✗ history - {e}")
        import_errors.append(('history', e))
    
    try:
        from ui.pages import risk_analysis
        print("  ✓ risk_analysis")
    except Exception as e:
        print(f"  ✗ risk_analysis - {e}")
        import_errors.append(('risk_analysis', e))
    
    try:
        from ui.pages import heatmap
        print("  ✓ heatmap")
    except Exception as e:
        print(f"  ✗ heatmap - {e}")
        import_errors.append(('heatmap', e))
    
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if missing_pages:
        print(f"\n⚠️  Missing {len(missing_pages)} page file(s):")
        for page in missing_pages:
            print(f"  - {page}")
    
    if import_errors:
        print(f"\n❌ {len(import_errors)} import error(s):")
        for module, error in import_errors:
            print(f"  - {module}: {error}")
    
    if not missing_pages and not import_errors:
        print("\n✓ All UI files verified successfully!")
        return True
    else:
        print("\n⚠️  Some UI files have issues")
        return False


if __name__ == "__main__":
    success = verify_ui_structure()
    sys.exit(0 if success else 1)
