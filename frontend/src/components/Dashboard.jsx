import React, { useEffect, useState } from 'react';
import { LayoutDashboard, Users, GitCompare, CheckCircle2, ShieldAlert, Target, Activity, ArrowUpRight, MapPin } from 'lucide-react';
import { api } from '../services/api';

export default function Dashboard({ role, district, setActiveTab, onSelectCase }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [role, district]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const res = await api.getDashboard(role, district);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-16 text-slate-400 text-sm">Loading intelligence dashboard...</div>;
  }

  const m = data?.metrics || {};
  const districtStats = data?.district_stats || {};

  return (
    <div className="space-y-6">
      {/* Metric Cards Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
        <MetricCard
          title="TOTAL OPEN CASES"
          value={m.total_open_cases}
          subtitle={`Missing: ${m.open_missing} • Found: ${m.open_found}`}
          icon={Users}
          color="from-blue-500 to-indigo-600"
          onClick={() => setActiveTab('cases')}
        />

        <MetricCard
          title="PROBABLE MATCHES"
          value={m.probable_matches}
          subtitle="Pending IO Verification"
          icon={GitCompare}
          color="from-amber-500 to-orange-600"
          onClick={() => setActiveTab('matches')}
        />

        <MetricCard
          title="VERIFIED LINKS"
          value={m.verified_links}
          subtitle="Joint District Alerts Sent"
          icon={CheckCircle2}
          color="from-emerald-500 to-teal-600"
        />

        <MetricCard
          title="FLAGGED CLUSTERS"
          value={m.flagged_clusters}
          subtitle="Trafficking Syndicates"
          icon={ShieldAlert}
          color="from-rose-500 to-pink-600"
          onClick={() => setActiveTab('graph')}
        />

        <MetricCard
          title="MATCH PRECISION@5"
          value={m.precision_at_5_percentage}
          subtitle="Evaluated on Seed Set"
          icon={Target}
          color="from-purple-500 to-violet-600"
        />
      </div>

      {/* District Breakdown & Trafficking Syndicate Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* District Activity Breakdown */}
        <div className="lg:col-span-6 glass-card p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-amber-400" />
              <span>District Intelligence Load</span>
            </span>
            <span className="text-xs text-slate-400">4 Active Districts</span>
          </h3>

          <div className="space-y-3">
            {Object.entries(districtStats).map(([distName, stats]) => (
              <div key={distName} className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-white">📍 {distName}</span>
                  <span className="font-mono font-bold text-amber-400">{stats.total} total cases</span>
                </div>
                <div className="flex text-[11px] text-slate-400 space-x-3">
                  <span>Missing: <strong className="text-rose-400">{stats.missing}</strong></span>
                  <span>Found/Rescued: <strong className="text-emerald-400">{stats.found}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Audit Event Activity Stream */}
        <div className="lg:col-span-6 glass-card p-5 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-amber-400" />
              <span>Real-Time Audit Stream</span>
            </span>
            <button onClick={() => setActiveTab('audit')} className="text-xs text-amber-400 hover:underline flex items-center">
              <span>View full log</span>
              <ArrowUpRight className="w-3 h-3 ml-0.5" />
            </button>
          </h3>

          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
            {(data?.recent_activity || []).map((act) => (
              <div key={act.id} className="p-2.5 bg-slate-950/70 rounded-lg border border-slate-800/80 text-xs flex justify-between items-center">
                <div className="space-y-0.5">
                  <div className="flex items-center space-x-1.5">
                    <span className="font-bold text-slate-200">{act.action}</span>
                    <span className="text-[10px] bg-slate-800 text-amber-400 px-1.5 py-0.2 rounded font-mono">{act.role}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">{act.district} • Target ID: {act.target_id || 'System'}</p>
                </div>
                <span className="text-[10px] text-slate-500 font-mono">
                  {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, subtitle, icon: Icon, color, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`glass-card glass-card-hover p-4 flex flex-col justify-between space-y-2 relative overflow-hidden group ${
        onClick ? 'cursor-pointer' : ''
      }`}
    >
      <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${color} opacity-10 blur-xl rounded-full group-hover:opacity-20 transition-all`} />

      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold tracking-wider text-slate-400 uppercase">{title}</span>
        <div className={`p-2 rounded-lg bg-gradient-to-br ${color} text-white shadow-md`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div>
        <p className="text-2xl font-extrabold text-white font-mono tracking-tight">{value}</p>
        <p className="text-[11px] text-slate-400 font-medium mt-0.5">{subtitle}</p>
      </div>
    </div>
  );
}
