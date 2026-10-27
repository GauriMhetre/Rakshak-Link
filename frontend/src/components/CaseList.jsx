import React, { useState, useEffect } from 'react';
import { Users, Search, Filter, MapPin, Calendar, GitCompare, Lock, Eye, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function CaseList({ role, district, onSelectCase, setActiveTab }) {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState('');
  const [districtFilter, setDistrictFilter] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadCases();
  }, [typeFilter, districtFilter, role, district]);

  const loadCases = async () => {
    setLoading(true);
    try {
      // Note: We pass district through the api function params, not as a query filter
      const filterDistrict = districtFilter || district; // Use selected district or fall back to user's district
      const data = await api.getCases(
        { type: typeFilter || undefined, search: search || undefined },
        role,
        filterDistrict
      );
      setCases(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadCases();
  };

  return (
    <div className="space-y-6">
      {/* Top Filter Bar */}
      <div className="glass-card p-4 flex flex-col md:flex-row gap-4 items-center justify-between bg-darkblue/30 border border-ashgray/10">
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <div className="p-2 bg-earth/10 text-earth rounded-lg">
            <Users className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-ashgray">Case Directory</h2>
            <p className="text-xs text-ashgray/70">Scoped view for <span className="text-earth font-semibold">{role} ({district})</span></p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2 w-full md:w-auto items-center">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 text-ashgray/50 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search name, ID, marks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-darkblue/40 border border-earth/20 rounded-lg text-xs text-ashgray focus:outline-none focus:border-earth/60"
            />
          </form>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-darkblue/40 border border-earth/20 text-xs text-ashgray px-3 py-1.5 rounded-lg focus:outline-none"
          >
            <option value="">All Types (Missing & Found)</option>
            <option value="MISSING">Missing Only</option>
            <option value="FOUND">Found Only</option>
          </select>

          <select
            value={districtFilter}
            onChange={(e) => setDistrictFilter(e.target.value)}
            className="bg-darkblue/40 border border-earth/20 text-xs text-ashgray px-3 py-1.5 rounded-lg focus:outline-none"
          >
            <option value="">All Districts</option>
            <option value="Pune">Pune</option>
            <option value="Mumbai Suburban">Mumbai Suburban</option>
            <option value="Thane">Thane</option>
            <option value="Nagpur">Nagpur</option>
          </select>
        </div>
      </div>

      {/* Case Grid */}
      {loading ? (
        <div className="text-center py-12 text-ashgray/70 text-sm">Loading cases...</div>
      ) : cases.length === 0 ? (
        <div className="glass-card p-12 text-center text-ashgray/70 space-y-2 bg-darkblue/20 border border-ashgray/10">
          <AlertCircle className="w-8 h-8 text-earth mx-auto opacity-60" />
          <p className="font-semibold text-ashgray">No cases match the current filter criteria</p>
          <p className="text-xs">Try clearing search filters or changing the target district.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cases.map((c) => {
            const isMissing = c.type === 'MISSING';
            const isMatched = c.status === 'MATCHED';

            return (
              <div
                key={c.id}
                className="glass-card glass-card-hover p-4 flex flex-col justify-between space-y-3 relative group bg-darkblue/30 border border-ashgray/10"
              >
                <div>
                  {/* Card Header Badges */}
                  <div className="flex items-center justify-between mb-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                      isMissing ? 'bg-earth/20 text-earth border border-earth/40' : 'bg-ashgray/20 text-ashgray border border-ashgray/40'
                    }`}>
                      {c.type}
                    </span>

                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                      isMatched ? 'bg-earth/30 text-earth border border-earth/60 font-bold' : 'bg-darkblue/60 text-ashgray/70 border border-darkblue/40'
                    }`}>
                      {c.status}
                    </span>
                  </div>

                  {/* Profile info & Photo */}
                  <div className="flex space-x-3 items-start">
                    <div className="w-16 h-16 rounded-lg bg-darkblue/60 border border-earth/20 overflow-hidden relative shrink-0 flex items-center justify-center">
                      {c.photo_url ? (
                        <img src={c.photo_url} alt={c.name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="text-center p-1 text-[9px] text-earth flex flex-col items-center">
                          <Lock className="w-4 h-4 mb-0.5 text-earth" />
                          <span>Embedding Only</span>
                        </div>
                      )}
                    </div>

                    <div className="min-w-0 flex-1">
                      <h3 className="text-sm font-bold text-ashgray truncate">{c.name}</h3>
                      {c.devanagari_name && (
                        <p className="text-xs text-earth/90 font-medium">{c.devanagari_name}</p>
                      )}
                      <p className="text-xs text-ashgray/70 mt-0.5">
                        {c.age} yrs • {c.sex} • {c.height_cm} cm
                      </p>
                      <p className="text-[11px] text-ashgray/50 truncate font-mono mt-0.5">{c.case_number}</p>
                    </div>
                  </div>

                  {/* Attributes */}
                  <div className="mt-3 pt-3 border-t border-earth/10 space-y-1 text-xs">
                    <div className="flex items-center text-ashgray space-x-1.5 truncate">
                      <MapPin className="w-3.5 h-3.5 text-earth shrink-0" />
                      <span className="truncate">{c.last_seen_found_place}</span>
                    </div>

                    <div className="flex items-center text-ashgray/70 space-x-1.5 text-[11px]">
                      <Calendar className="w-3.5 h-3.5 text-ashgray/50 shrink-0" />
                      <span>{new Date(c.last_seen_found_time).toLocaleDateString()}</span>
                      <span className="text-ashgray/40">•</span>
                      <span className="font-semibold text-ashgray">📍 {c.district}</span>
                    </div>

                    {c.marks && (
                      <p className="text-[11px] text-ashgray/70 line-clamp-1 italic bg-darkblue/40 p-1.5 rounded mt-1 border border-earth/10">
                        "{c.marks}"
                      </p>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <button
                  onClick={() => {
                    if (onSelectCase) onSelectCase(c);
                    setActiveTab('matches');
                  }}
                  className="w-full py-2 bg-darkblue/60 hover:bg-earth hover:text-darkblue text-ashgray text-xs font-bold rounded-lg transition-all flex items-center justify-center space-x-1.5 group-hover:border-earth/50 border border-earth/20"
                >
                  <GitCompare className="w-3.5 h-3.5" />
                  <span>Run Match Review</span>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
