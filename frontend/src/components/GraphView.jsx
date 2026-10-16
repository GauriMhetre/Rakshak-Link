import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { Share2, AlertTriangle, ShieldAlert, Phone, MapPin, Info, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function GraphView({ role, district }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedElement, setSelectedElement] = useState(null);

  useEffect(() => {
    loadGraph();
  }, [role, district]);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const data = await api.getGraph(role, district);
      setGraphData(data);
      initCytoscape(data.elements);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const initCytoscape = (elements) => {
    if (!containerRef.current) return;

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#f8fafc',
            'font-size': '10px',
            'font-weight': 'bold',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'background-color': '#475569',
            'border-width': 2,
            'border-color': '#1e293b',
          }
        },
        {
          selector: 'node.missing',
          style: {
            'background-color': '#f43f5e',
            'border-color': '#9f1239',
            'width': 28,
            'height': 28,
          }
        },
        {
          selector: 'node.found',
          style: {
            'background-color': '#10b981',
            'border-color': '#065f46',
            'width': 28,
            'height': 28,
          }
        },
        {
          selector: 'node-phone',
          style: {
            'background-color': '#f59e0b',
            'border-color': '#78350f',
            'width': 34,
            'height': 34,
            'shape': 'diamond',
          }
        },
        {
          selector: 'node-location',
          style: {
            'background-color': '#8b5cf6',
            'border-color': '#4c1d95',
            'width': 30,
            'height': 30,
            'shape': 'hexagon',
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#334155',
            'curve-style': 'bezier',
            'opacity': 0.7,
          }
        },
        {
          selector: 'edge.edge-phone',
          style: {
            'line-color': '#f59e0b',
            'line-style': 'dashed',
            'width': 2,
          }
        },
        {
          selector: 'edge.edge-verified',
          style: {
            'line-color': '#10b981',
            'width': 3.5,
          }
        },
        {
          selector: ':selected',
          style: {
            'border-width': 4,
            'border-color': '#38bdf8',
            'shadow-blur': 12,
            'shadow-color': '#38bdf8',
          }
        }
      ],
      layout: {
        name: 'cose',
        animate: false,
        padding: 30,
        nodeOverlap: 20,
        componentSpacing: 40,
      }
    });

    cy.on('tap', 'node, edge', (evt) => {
      const item = evt.target;
      setSelectedElement(item.data());
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedElement(null);
      }
    });

    cyRef.current = cy;
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="glass-card p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-purple-500/10 text-purple-400 rounded-xl border border-purple-500/20">
            <Share2 className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-ashgray">Interstate Trafficking Network Graph</h2>
            <p className="text-xs text-ashgray/70">Interactive Cytoscape network mapping shared phones, locations, and verified cross-district links.</p>
          </div>
        </div>

        <button
          onClick={loadGraph}
          className="px-3 py-1.5 bg-darkblue/40 border border-earth/20 hover:border-amber-500 text-ashgray text-xs font-bold rounded-lg transition-all flex items-center space-x-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Network Layout</span>
        </button>
      </div>

      {/* Flagged Trafficking Clusters Banner */}
      {graphData?.flagged_clusters?.length > 0 && (
        <div className="p-4 bg-amber-500/10 border border-amber-500/40 rounded-xl space-y-2">
          <div className="flex items-center space-x-2 text-earth font-extrabold text-sm">
            <ShieldAlert className="w-5 h-5 text-earth" />
            <span>CRITICAL TRAFFICKING SYNDICATE ALERTS ({graphData.flagged_clusters.length} FLAGGED CLUSTERS)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            {graphData.flagged_clusters.map((c) => (
              <div key={c.cluster_id} className="p-3 bg-darkblue/40/80 rounded-lg border border-amber-500/30 text-xs space-y-1">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-earth">{c.cluster_id} • Shared {c.shared_node_type.toUpperCase()}</span>
                  <span className="px-2 py-0.5 bg-rose-500/20 text-rose-300 font-bold rounded text-[10px]">{c.risk_level} RISK</span>
                </div>
                <p className="font-mono text-ashgray">Value: {c.shared_value}</p>
                <p className="text-ashgray/70">Linked to <strong className="text-ashgray">{c.case_count} cases</strong> across districts: <span className="text-amber-300">{c.districts.join(', ')}</span></p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Graph Canvas & Details Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 glass-card p-4 relative min-h-[500px]">
          <div className="absolute top-4 left-4 z-10 flex space-x-2 bg-darkblue/40/90 p-2 rounded-lg border border-earth/20 text-[11px]">
            <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> <span className="text-ashgray">Missing</span></span>
            <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> <span className="text-ashgray">Found</span></span>
            <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 bg-amber-500 rotate-45" /> <span className="text-ashgray">Phone</span></span>
            <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 bg-purple-500" /> <span className="text-ashgray">Location</span></span>
          </div>

          <div ref={containerRef} className="w-full h-[520px] rounded-lg" />
        </div>

        {/* Inspection Sidebar */}
        <div className="lg:col-span-4 glass-card p-5 space-y-4">
          <h3 className="text-sm font-bold text-ashgray flex items-center space-x-2 pb-3 border-b border-earth/20">
            <Info className="w-4 h-4 text-earth" />
            <span>Graph Element Inspector</span>
          </h3>

          {selectedElement ? (
            <div className="space-y-3 text-xs">
              <div className="p-3 bg-darkblue/40 rounded-lg border border-earth/20">
                <span className="text-[10px] text-earth uppercase font-bold block">{selectedElement.type || 'Connection Edge'}</span>
                <p className="text-sm font-bold text-ashgray">{selectedElement.label}</p>
              </div>

              {selectedElement.district && (
                <div className="flex justify-between text-ashgray py-1 border-b border-earth/20">
                  <span>District:</span>
                  <span className="font-bold text-earth">{selectedElement.district}</span>
                </div>
              )}

              {selectedElement.age && (
                <div className="flex justify-between text-ashgray py-1 border-b border-earth/20">
                  <span>Age / Sex:</span>
                  <span className="font-bold text-ashgray">{selectedElement.age} yrs • {selectedElement.sex}</span>
                </div>
              )}

              {selectedElement.phone_numbers?.length > 0 && (
                <div className="space-y-1">
                  <span className="text-ashgray/70 text-[11px] block">Associated Phone Numbers:</span>
                  <div className="space-y-1">
                    {selectedElement.phone_numbers.map(p => (
                      <div key={p} className="p-1.5 bg-darkblue/40 rounded text-amber-300 font-mono text-[11px] border border-earth/20">
                        📞 {p}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-ashgray/70 text-xs">
              Click any node or edge on the graph to inspect detailed attributes and connected cases.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
