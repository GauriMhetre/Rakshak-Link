import React, { useEffect, useState } from 'react';
import { FileText, Shield, UserCheck, Calendar } from 'lucide-react';
import { api } from '../services/api';

export default function AuditLogView({ role, district }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAudit();
  }, [role, district]);

  const loadAudit = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs(role, district);
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="glass-card p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-500/10 text-earth rounded-xl border border-amber-500/20">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-ashgray">Immutable District Audit Trail</h2>
            <p className="text-xs text-ashgray/70">Scoped access log enforcing zero-trust audit compliance across all search & match decisions.</p>
          </div>
        </div>
      </div>

      <div className="glass-card p-4 overflow-x-auto">
        {loading ? (
          <div className="text-center py-12 text-ashgray/70 text-sm">Loading audit logs...</div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-earth/20 text-ashgray/70 font-bold uppercase text-[10px] tracking-wider">
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">User Role</th>
                <th className="py-2.5 px-3">District</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Target ID</th>
                <th className="py-2.5 px-3">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-ashgray">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-darkblue/40/60 transition-colors">
                  <td className="py-2.5 px-3 whitespace-nowrap text-ashgray/70">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap">
                    <span className="px-2 py-0.5 bg-darkblue/40 text-earth border border-earth/20 rounded font-semibold text-[11px]">
                      {log.user_role}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap font-bold text-ashgray">
                    📍 {log.user_district}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap font-bold text-emerald-400">
                    {log.action}
                  </td>
                  <td className="py-2.5 px-3 whitespace-nowrap text-ashgray/70">
                    {log.target_id || '-'}
                  </td>
                  <td className="py-2.5 px-3 text-ashgray/70 max-w-xs truncate">
                    {JSON.stringify(log.details || {})}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
