# ============================================================================
# INTEGRATION GUIDE: Comprehensive Risk Assessment
# ============================================================================

This guide explains how to integrate the comprehensive risk assessment into your
Land Evaluation AI application.

## What's Been Added:

1. **Comprehensive Risk Assessment Module** (`data/feature_extraction/risk_assessment.py`)
   - Evaluates 7 types of risks:
     * Flood Risk
     * Landslide Risk
     * Erosion Risk
     * Seismic Risk (Algeria-specific zones)
     * Drought Risk
     * Wildfire Risk
     * Subsidence Risk

2. **Risk Dashboard UI Component** (`ui/components/risk_dashboard.py`)
   - Visual risk cards for each risk type
   - Overall risk summary
   - Risk severity comparison chart
   - Mitigation recommendations

3. **Updated Environmental Features** (`data/feature_extraction/environmental_features_updated.py`)
   - Now includes comprehensive risk assessment
   - Passes terrain features for better risk calculation

## Integration Steps:

### Step 1: Update environmental_features.py

Replace your current `data/feature_extraction/environmental_features.py` with the content from
`environmental_features_updated.py`:

```python
# In environmental_features.py, add:
from data.feature_extraction.risk_assessment import ComprehensiveRiskAssessment

# In __init__:
self.risk_assessor = ComprehensiveRiskAssessment()

# Update extract() method to accept terrain_features parameter
def extract(self, geometry: ee.Geometry, terrain_features: Dict = None) -> Dict:
    # ... existing code ...
    
    # Add comprehensive risk assessment
    features_for_risk = {
        'terrain': terrain_features or {},
        'environmental': {**ndvi, **land_cover, **water}
    }
    comprehensive_risks = self.risk_assessor.assess_all_risks(geometry, features_for_risk)
    
    return {
        # ... existing returns ...
        'comprehensive_risks': comprehensive_risks,  # NEW
    }
```

### Step 2: Update analysis_processor.py

Modify the `_extract_all_features` method to pass terrain to environmental:

```python
# In _extract_all_features:

# First extract terrain
features['terrain'] = self.terrain_extractor.extract(ee_geometry)

# Then pass terrain to environmental extractor
features['environmental'] = self.env_extractor.extract(
    ee_geometry,
    terrain_features=features['terrain']  # Pass terrain here
)
```

### Step 3: Update results.py

Add the risk dashboard to your results page:

```python
# At the top of ui/pages/results.py
from ui.components.risk_dashboard import render_comprehensive_risks, render_risk_summary_metrics

# In render() function, after summary metrics:
def render():
    # ... existing code ...
    
    # Add risk summary metrics
    render_risk_summary_metrics(results)
    
    st.markdown("---")
    
    # Add comprehensive risk dashboard
    render_comprehensive_risks(results)
    
    st.markdown("---")
    
    # ... rest of existing code ...
```

### Step 4: Update score_aggregator.py

Enhance risk assessment to use comprehensive risks:

```python
# In _assess_risks method:
def _assess_risks(self, features: Dict) -> Dict:
    """Assess development risks using comprehensive assessment"""
    
    env = features.get('environmental', {})
    comprehensive_risks = env.get('comprehensive_risks', {})
    
    if comprehensive_risks:
        overall = comprehensive_risks.get('overall', {})
        
        # Count high severity risks
        high_count = overall.get('high_risk_count', 0)
        medium_count = overall.get('medium_risk_count', 0)
        
        # Determine overall risk level
        if high_count >= 3:
            risk_level = 'very_high'
        elif high_count >= 2:
            risk_level = 'high'
        elif high_count >= 1 or medium_count >= 3:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Collect all risk descriptions
        all_risks = []
        for risk_type in ['flood', 'landslide', 'erosion', 'seismic', 'drought', 'wildfire', 'subsidence']:
            risk_data = comprehensive_risks.get(risk_type, {})
            if risk_data.get('severity', 0) >= 3:  # Medium or higher
                all_risks.append(f"{risk_type.title()}: {risk_data.get('description', '')}")
        
        return {
            'level': risk_level,
            'risks': all_risks,
            'risk_count': len(all_risks),
            'comprehensive_data': comprehensive_risks
        }
    
    # Fallback to simple assessment if comprehensive not available
    # ... existing simple assessment code ...
```

## Testing:

After integration, test with:

1. **Flat coastal area** - Should show high flood risk, possible seismic risk
2. **Mountainous area** - Should show landslide, erosion risks
3. **Southern Algeria** - Should show high drought risk
4. **Northern Algeria** - Should show seismic risk (Tell Atlas zone)

## Risk Level Interpretations:

### Flood Risk:
- Based on water occurrence, slope, elevation
- Very High (60-100): Frequent flooding expected
- High (40-60): Flooding likely during heavy rain
- Medium (20-40): Occasional flooding possible
- Low (10-20): Unlikely under normal conditions
- Very Low (0-10): Well-drained area

### Landslide Risk:
- Based on slope steepness, elevation variation, vegetation
- Very High (70-100): Unstable slopes, critical risk
- High (50-70): Slope stabilization essential
- Medium (30-50): Engineering assessment needed
- Low (15-30): Standard precautions sufficient
- Very Low (0-15): Stable terrain

### Erosion Risk:
- Based on slope and vegetation cover
- Very High (60-100): Rapid soil loss expected
- High (45-60): Protective measures essential
- Medium (25-45): Erosion control recommended
- Low (10-25): Basic measures sufficient
- Very Low (0-10): Stable soil

### Seismic Risk:
- Based on Algeria seismic zones
- Very High: Northern coastal (Algiers-Oran region)
- High: Northern Tell Atlas
- Medium: North-central plateau
- Low: Saharan region

### Drought Risk:
- Based on latitude and vegetation health
- Very High (70-100): Severe water scarcity
- High (50-70): Limited water resources
- Medium (30-50): Irrigation may be needed
- Low (15-30): Adequate water availability
- Very Low (0-15): Good water resources

### Wildfire Risk:
- Based on vegetation density and slope
- Very High (60-100): Critical fire risk
- High (45-60): Fire prevention essential
- Medium (30-45): Fire breaks recommended
- Low (15-30): Basic fire safety sufficient
- Very Low (0-15): Minimal fire threat

### Subsidence Risk:
- Based on elevation and soil characteristics
- High (50-100): Soil investigation required
- Medium (30-50): Foundation assessment recommended
- Low (15-30): Standard practices sufficient
- Very Low (0-15): Minimal subsidence expected

## Sample Output:

When properly integrated, the results page will show:

```
🛡️ Comprehensive Risk Assessment

📊 Overall Risk Profile
┌─────────────┬──────────────┬────────────────┐
│   Medium    │ Avg: 2.8/5   │ 1 High, 2 Med  │
└─────────────┴──────────────┴────────────────┘

✅ No major risks identified
📊 Overall Risk Level: Medium
📈 Average Risk Severity: 2.8/5

🔍 Detailed Risk Breakdown

🌊 Flood Risk - Low
   Risk Score: 15/100
   • Gentle slopes provide good drainage
   • No significant water occurrence detected

⛰️ Landslide Risk - Very Low
   Risk Score: 8/100
   • Gentle terrain - landslide risk minimal

🏗️ Seismic Risk - Medium
   Risk Score: 50/100
   • Located in Northern Algeria (Tell Atlas)
   • Seismic Zone III - building codes apply

🛠️ Risk Mitigation Recommendations
🏗️ Seismic: Follow seismic building codes, use flexible foundations
```

## Notes:

- The risk assessment requires Google Earth Engine to be available
- If EE is not available, default low-risk values will be used
- Seismic risk zones are Algeria-specific (can be extended for other countries)
- All risk scores are on 0-100 scale, severities on 1-5 scale

## Future Enhancements:

- Add historical disaster data for more accurate assessments
- Integrate real seismic hazard maps
- Add climate change projections for drought/flood risks
- Include insurance cost implications for each risk
- Add interactive risk maps showing spatial distribution
