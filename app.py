import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function App() {
  // Simulate Earth Engine availability state
  const [eeAvailable, setEeAvailable] = useState(false);
  
  // Simulate analysis results state
  const [analysisExists, setAnalysisExists] = useState(true);

  // Page navigation state
  const [currentPage, setCurrentPage] = useState('risk_analysis');

  // Animation variants for page transitions
  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.4, ease: 'easeOut' }
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      {/* Sidebar Navigation */}
      <motion.div 
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-64 bg-gradient-to-b from-[#1a5632] to-[#0f3420] text-white shadow-xl flex flex-col"
      >
        <div className="p-6 border-b border-[#2e8b57]/30">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">🌍</div>
            <div className="font-bold text-2xl tracking-tight">LandSense</div>
          </div>
          <div className="mt-1 text-sm text-[#a7f3d0]">Precision Land Analysis</div>
        </div>
        
        <nav className="p-4 space-y-2 flex-1">
          <SidebarButton 
            icon="🏠" 
            label="Home" 
            active={currentPage === 'home'}
            onClick={() => setCurrentPage('home')}
          />
          <SidebarButton 
            icon="🗺️" 
            label="New Analysis" 
            active={currentPage === 'analysis'}
            onClick={() => setCurrentPage('analysis')}
          />
          
          {analysisExists && (
            <>
              <SidebarButton 
                icon="📊" 
                label="View Results" 
                active={currentPage === 'results'}
                onClick={() => setCurrentPage('results')}
              />
              <SidebarButton 
                icon="🛡️" 
                label="Risk Assessment" 
                active={currentPage === 'risk_analysis'}
                onClick={() => setCurrentPage('risk_analysis')}
                highlight
              />
              <SidebarButton 
                icon="🗺️" 
                label="Suitability Heatmap" 
                active={currentPage === 'heatmap'}
                onClick={() => setCurrentPage('heatmap')}
              />
            </>
          )}
          
          <SidebarButton 
            icon="📜" 
            label="History" 
            active={currentPage === 'history'}
            onClick={() => setCurrentPage('history')}
          />
        </nav>
        
        <div className="p-4 border-t border-[#2e8b57]/30 mt-auto">
          <div className="flex items-center space-x-3 p-3 bg-[#0f3420]/70 rounded-lg">
            <div className="text-xl">⚙️</div>
            <div>
              <div className="font-medium">Earth Engine Status</div>
              <div className={`mt-1 flex items-center ${
                eeAvailable ? 'text-[#34d399]' : 'text-[#f87171]'
              }`}>
                {eeAvailable ? '✅ Online' : '❌ Offline'}
              </div>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-[#2e8b57]/20 text-xs text-[#a7f3d0]/80">
            <div>LandSense v2.1.0</div>
            <div>© 2026 Environmental Analytics</div>
          </div>
        </div>
      </motion.div>
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm p-4 flex items-center justify-between border-b">
          <h1 className="text-2xl font-bold text-[#1a5632]">Risk Assessment</h1>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-500">Friday, January 30, 2026</div>
            <div className="w-10 h-10 rounded-full bg-[#dbeafe] flex items-center justify-center text-[#1d4ed8] font-medium">
              LS
            </div>
          </div>
        </header>
        
        <motion.main 
          variants={pageVariants}
          initial="initial"
          animate="animate"
          className="flex-1 p-8 overflow-auto"
        >
          {currentPage === 'risk_analysis' && (
            <div className="max-w-4xl mx-auto">
              {/* Error State Card */}
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="bg-white rounded-2xl shadow-lg border border-yellow-100 overflow-hidden"
              >
                <div className="bg-gradient-to-r from-yellow-50 to-amber-50 border-b border-yellow-200 p-6 flex items-start">
                  <div className="text-5xl mr-4 mt-1">⚠️</div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">Comprehensive risk assessment data not available</h2>
                    <p className="mt-2 text-gray-600 max-w-2xl">
                      Risk assessment requires Google Earth Engine to be properly configured to access satellite data and geospatial analysis tools.
                    </p>
                  </div>
                </div>
                
                <div className="p-8">
                  <div className="grid md:grid-cols-2 gap-10">
                    {/* Why Section */}
                    <div>
                      <div className="flex items-center mb-4">
                        <div className="text-xl font-bold text-[#1e40af] mr-3">❓</div>
                        <h3 className="text-xl font-bold text-gray-800">Why?</h3>
                      </div>
                      <div className="space-y-4 text-gray-700 pl-8 border-l-2 border-[#3b82f6]/20 py-2">
                        <p className="flex">
                          <span className="font-medium mr-2">•</span>
                          Google Earth Engine provides essential satellite imagery and geospatial datasets required for accurate risk modeling
                        </p>
                        <p className="flex">
                          <span className="font-medium mr-2">•</span>
                          Without GEE integration, the system cannot access historical climate data, terrain analysis, or environmental change detection
                        </p>
                        <p className="flex">
                          <span className="font-medium mr-2">•</span>
                          Risk algorithms require high-resolution geospatial data that's only available through Earth Engine's planetary-scale database
                        </p>
                      </div>
                    </div>
                    
                    {/* What to do Section */}
                    <div>
                      <div className="flex items-center mb-4">
                        <div className="text-xl font-bold text-[#047857] mr-3">✅</div>
                        <h3 className="text-xl font-bold text-gray-800">What to do?</h3>
                      </div>
                      <div className="space-y-5 text-gray-700 pl-8 border-l-2 border-[#10b981]/20 py-2">
                        <div className="flex">
                          <div className="font-bold mr-3 mt-1">1.</div>
                          <div>
                            <div className="font-medium text-[#047857]">Configure GEE in Streamlit secrets</div>
                            <div className="mt-1 text-sm text-gray-600">
                              Add your service account credentials to Streamlit Secrets Manager with key <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded">GEE_SERVICE_ACCOUNT_JSON</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex">
                          <div className="font-bold mr-3 mt-1">2.</div>
                          <div>
                            <div className="font-medium text-[#047857]">Re-run your land analysis</div>
                            <div className="mt-1 text-sm text-gray-600">
                              Return to the analysis page and process your boundary data again with Earth Engine enabled
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex">
                          <div className="font-bold mr-3 mt-1">3.</div>
                          <div>
                            <div className="font-medium text-[#047857]">Access comprehensive risk assessment</div>
                            <div className="mt-1 text-sm text-gray-600">
                              The system will automatically generate detailed risk profiles including flood zones, fire hazards, soil stability, and climate vulnerability
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-10 pt-8 border-t border-gray-100 flex justify-center">
                    <motion.button
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setCurrentPage('analysis')}
                      className="bg-gradient-to-r from-[#1a5632] to-[#0f3420] text-white font-bold py-4 px-8 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 flex items-center"
                    >
                      <span className="text-xl mr-3">➡️</span>
                      Go to New Analysis Page
                    </motion.button>
                  </div>
                </div>
                
                <div className="bg-[#f0fdf4] border-t border-[#bbf7d0] p-4 text-center text-sm text-[#166534]">
                  <div className="font-medium">💡 Tip:</div>
                  <div className="mt-1">For local development, run <span className="font-mono bg-white px-2 py-1 rounded">earthengine authenticate</span> in your terminal to enable Earth Engine access</div>
                </div>
              </motion.div>
              
              {/* Informational Note */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="mt-8 bg-[#eff6ff] border border-[#bfdbfe] rounded-xl p-6"
              >
                <div className="flex">
                  <div className="text-3xl mr-4">ℹ️</div>
                  <div>
                    <h3 className="font-bold text-lg text-[#1e40af] mb-2">About Risk Assessment</h3>
                    <p className="text-gray-700">
                      When Earth Engine is properly configured, LandSense provides comprehensive risk analysis including:
                    </p>
                    <ul className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 text-gray-700">
                      <li className="flex items-start">
                        <span className="text-[#10b981] font-bold mr-2 mt-1">✓</span>
                        <span>Flood zone mapping and historical inundation patterns</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[#10b981] font-bold mr-2 mt-1">✓</span>
                        <span>Wildfire risk assessment based on vegetation and climate data</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[#10b981] font-bold mr-2 mt-1">✓</span>
                        <span>Soil erosion and landslide vulnerability analysis</span>
                      </li>
                      <li className="flex items-start">
                        <span className="text-[#10b981] font-bold mr-2 mt-1">✓</span>
                        <span>Climate change impact projections for your land area</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
          
          {currentPage !== 'risk_analysis' && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-6">✨</div>
                <h2 className="text-3xl font-bold text-gray-800 mb-4">LandSense Navigation</h2>
                <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                  Select a page from the sidebar to view content. The Risk Assessment page requires Google Earth Engine to be properly configured to display comprehensive analysis.
                </p>
                <div className="mt-8 flex justify-center">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setCurrentPage('risk_analysis')}
                    className="bg-[#1a5632] text-white font-bold py-3 px-8 rounded-lg shadow-md hover:bg-[#164e2e] transition-colors"
                  >
                    View Risk Assessment Page
                  </motion.button>
                </div>
              </div>
            </div>
          )}
        </motion.main>
        
        {/* Footer */}
        <footer className="bg-white border-t p-4 text-center text-sm text-gray-500">
          LandSense Environmental Analytics Platform • Data Sources: NASA, USGS, ESA, NOAA • 
          <span className="ml-2 text-[#1a5632] font-medium">Earth Engine Integration Required for Full Analysis</span>
        </footer>
      </div>
    </div>
  );
}

// Reusable Sidebar Button Component
function SidebarButton({ icon, label, active, onClick, highlight }) {
  return (
    <motion.button
      whileHover={{ x: 5 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full flex items-center p-3 rounded-lg text-left transition-all ${
        active 
          ? `bg-[#2e8b57] text-white shadow-md ${highlight ? 'ring-2 ring-[#86efac] ring-offset-2' : ''}` 
          : 'bg-transparent hover:bg-[#244a35]/30 text-gray-200'
      }`}
    >
      <span className="text-xl mr-3 min-w-[28px]">{icon}</span>
      <span className="font-medium">{label}</span>
      {highlight && active && (
        <span className="ml-auto bg-[#86efac] text-[#064e3b] text-xs font-bold px-2 py-1 rounded-full">
          NEW
        </span>
      )}
    </motion.button>
  );
}
