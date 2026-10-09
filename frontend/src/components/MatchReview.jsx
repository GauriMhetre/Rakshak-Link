import React, { useState, useEffect } from 'react';
import { GitCompare, CheckCircle, XCircle, AlertTriangle, ShieldCheck, ArrowRight, Activity, MapPin, Calendar, Lock } from 'lucide-react';
import { api } from '../services/api';

export default function MatchReview({ selectedCase, role, district, setActiveTab }) {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeMatch, setActiveMatch] = useState(null);
  const [rejectionModalOpen, setRejectionModalOpen] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [actionSuccess, setActionSuccess] = useState('');
  const [actionError, setActionError] = useState('');

  useEffect(() => {
    if (selectedCase) {
      loadMatches(selectedCase.id);
    }
  }, [selectedCase, role, district]);

  const loadMatches = async (caseId) => {
    setLoading(true);
    setActionSuccess('');
    setActionError('');
    try {
      const data = await api.getMatchesForCase(caseId, role, district);
      setMatches(data);
      if (data.length > 0) {
        setActiveMatch(data[0]);
      } else {
        setActiveMatch(null);
      }
    } catch (err) {
      setActionError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!activeMatch) return;
    setActionSuccess('');
    setActionError('');
    try {
      const res = await api.verifyMatch(activeMatch.id, 'Verified by IO across districts', role, district);
      setActionSuccess(res.message);
      // Reload matches
      loadMatches(selectedCase.id);
    } catch (err) {
      setActionError(err.message);
    }
  };

  const handleRejectSubmit = async (e) => {
    e.preventDefault();
    if (!activeMatch || !rejectionReason.trim()) return;
    setActionSuccess('');
    setActionError('');
    try {
      const res = await api.rejectMatch(activeMatch.id, rejectionReason, role, district);
      setActionSuccess(res.message);
      setRejectionModalOpen(false);
      setRejectionReason('');
      loadMatches(selectedCase.id);
    } catch (err) {
      setActionError(err.message);
    }
  };

  if (!selectedCase) {
    return (
      <div className="glass-card p-12 text-center text-slate-400 space-y-3">
        <GitCompare className="w-10 h-10 text-amber-500 mx-auto opacity-70" />
        <h3 className="text-lg font-bold text-white">No Case Selected for Match Review</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">Select a case from the Case Directory to evaluate multi-signal candidate matches across Pune, Mumbai, Thane & Nagpur.</p>
        <button
          onClick={() => setActiveTab('cases')}
          className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-lg transition-all"
        >
          Go to Case Directory
        </button>
      </div>
    );
  }

  const sCase = activeMatch?.source_case || selectedCase;
  const tCase = activeMatch?.target_case || (sCase.id === selectedCase.id ? null : selectedCase);
  const bd = activeMatch?.score_breakdown || { face_score: 0, name_score: 0, attr_score: 0, geotime_score: 0, details: {} };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-card p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <GitCompare className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-white">Multi-Signal Candidate Match Evaluator</h2>
              <span className="text-[10px] bg-slate-800 text-slate-300 font-mono px-2 py-0.5 rounded">{selectedCase.case_number}</span>
            </div>
            <p className="text-xs text-slate-400">Evaluating target query: <strong className="text-amber-400">{selectedCase.name}</strong> ({selectedCase.district})</p>
          </div>
        </div>

        {/* Candidate selector buttons */}
        <div className="flex items-center space-x-2 overflow-x-auto w-full md:w-auto">
          {matches.map((m, idx) => {
            const isSel = activeMatch?.id === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setActiveMatch(m)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 whitespace-nowrap ${
                  isSel
                    ? 'bg-amber-500 text-slate-950 shadow-lg'
                    : 'bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800'
                }`}
              >
                <span>Candidate #{idx + 1}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                  isSel ? 'bg-slate-950/30 text-slate-950' : 'bg-slate-800 text-amber-400'
                }`}>
                  {intPct(m.score)}%
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {actionSuccess && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 rounded-xl flex items-center space-x-3 text-sm">
          <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
          <p className="font-semibold">{actionSuccess}</p>
        </div>
      )}

      {actionError && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl flex items-center space-x-3 text-sm">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <p>{actionError}</p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Evaluating candidate matches...</div>
      ) : !activeMatch ? (
        <div className="glass-card p-12 text-center text-slate-400 space-y-2">
          <AlertTriangle className="w-8 h-8 text-amber-500 mx-auto opacity-70" />
          <p className="font-semibold text-white">No Probable Candidates Above Confidence Threshold (60%)</p>
          <p className="text-xs">The system continues monitoring incoming intake reports across all districts.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Side-by-side Case Records */}
          <div className="lg:col-span-8 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Primary Query Case */}
              <CaseSideCard caseData={sCase} isPrimary={true} currentDistrict={district} />

              {/* Candidate Found Case */}
              <CaseSideCard caseData={tCase} isPrimary={false} currentDistrict={district} />
            </div>

            {/* Verification Actions */}
            <div className="glass-card p-4 flex flex-col sm:flex-row items-center justify-between gap-4 border-amber-500/30">
              <div className="text-xs text-slate-400">
                <p className="font-bold text-white">Human-in-the-Loop Safeguard</p>
                <p>Verify links cases and sends joint alert to both districts. Rejection feeds feedback table.</p>
              </div>

              <div className="flex items-center space-x-3 w-full sm:w-auto">
                <button
                  onClick={() => setRejectionModalOpen(true)}
                  disabled={activeMatch.status === 'VERIFIED' || activeMatch.status === 'REJECTED'}
                  className="flex-1 sm:flex-initial px-4 py-2.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 font-bold text-xs rounded-xl transition-all flex items-center justify-center space-x-1.5 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject Match</span>
                </button>

                <button
                  onClick={handleVerify}
                  disabled={activeMatch.status === 'VERIFIED'}
                  className="flex-1 sm:flex-initial px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-slate-950 font-extrabold text-xs rounded-xl shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center space-x-1.5 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4 stroke-[2.5]" />
                  <span>{activeMatch.status === 'VERIFIED' ? 'Verified Link' : 'Verify & Alert Districts'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Score Breakdown & Signal Radar */}
          <div className="lg:col-span-4 space-y-4">
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-amber-400" />
                  <span>Fused Score Breakdown</span>
                </h3>
                <span className="text-xl font-extrabold text-amber-400 font-mono">
                  {intPct(activeMatch.score)}%
                </span>
              </div>

              {/* Score Bar Indicators */}
              <div className="space-y-3 text-xs">
                <SignalBar label="Face Cosine Similarity" score={bd.face_score} weight="35%" color="bg-cyan-500" />
                <SignalBar label="Name Phonetic & Transliteration" score={bd.name_score} weight="25%" color="bg-amber-500" />
                <SignalBar label="Attribute Overlap (Age/Height/Marks)" score={bd.attr_score} weight="20%" color="bg-emerald-500" />
                <SignalBar label="Geo-Time Transport Plausibility" score={bd.geotime_score} weight="20%" color="bg-purple-500" />
              </div>

              {/* Explanatory Details */}
              <div className="pt-3 border-t border-slate-800 space-y-2 text-[11px] text-slate-400">
                <p className="font-semibold text-slate-300">Signal Explanations:</p>
                {bd.details?.geotime_details && (
                  <div className="bg-slate-950 p-2 rounded border border-slate-800 space-y-1 font-mono">
                    <p>📍 Distance: {bd.details.geotime_details.distance_km} km</p>
                    <p>⏱️ Time Diff: {bd.details.geotime_details.time_diff_hours} hrs</p>
                    <p>🚀 Req Speed: {bd.details.geotime_details.required_speed_kmh} km/h</p>
                  </div>
                )}

                {bd.details?.shared_phones?.length > 0 && (
                  <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded text-amber-300 font-semibold">
                    ⚠️ SHARED PHONE DETECTED: {bd.details.shared_phones.join(', ')} (+10% syndicate bonus)
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Rejection Modal */}
      {rejectionModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-bold text-white">Reject Candidate Match</h3>
            <p className="text-xs text-slate-400">Please provide a reason for rejecting this candidate. Feedback is recorded to fine-tune the matching engine weights.</p>

            <form onSubmit={handleRejectSubmit} className="space-y-4">
              <textarea
                required
                rows="3"
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="e.g. Physical marks do not match upon photo verification; wrong individual."
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:border-rose-500 focus:outline-none"
              />

              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setRejectionModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-lg hover:bg-slate-700"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="px-4 py-2 bg-rose-500 text-slate-950 font-bold text-xs rounded-lg hover:bg-rose-600"
                >
                  Confirm Rejection
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function CaseSideCard({ caseData, isPrimary, currentDistrict }) {
  if (!caseData) return null;
  const isMissing = caseData.type === 'MISSING';

  return (
    <div className={`glass-card p-4 space-y-3 border ${isPrimary ? 'border-amber-500/40' : 'border-slate-800'}`}>
      <div className="flex items-center justify-between">
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
          isMissing ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
        }`}>
          {isPrimary ? 'PRIMARY QUERY CASE' : 'MATCH CANDIDATE'} ({caseData.type})
        </span>

        <span className="text-[11px] font-semibold text-amber-400">📍 {caseData.district}</span>
      </div>

      <div className="flex space-x-3 items-start">
        <div className="w-20 h-20 bg-slate-950 border border-slate-800 rounded-lg overflow-hidden shrink-0 flex items-center justify-center">
          {caseData.photo_url ? (
            <img src={caseData.photo_url} alt={caseData.name} className="w-full h-full object-cover" />
          ) : (
            <div className="text-center p-1 text-[9px] text-amber-400 flex flex-col items-center">
              <Lock className="w-4 h-4 text-amber-500 mb-0.5" />
              <span>Cross-District Photo Protected</span>
            </div>
          )}
        </div>

        <div className="min-w-0 flex-1 space-y-0.5">
          <h4 className="text-base font-bold text-white truncate">{caseData.name}</h4>
          {caseData.devanagari_name && <p className="text-xs text-amber-400">{caseData.devanagari_name}</p>}
          <p className="text-xs text-slate-300">{caseData.age} yrs • {caseData.sex} • {caseData.height_cm} cm</p>
          <p className="text-[11px] text-slate-400 font-mono">{caseData.case_number}</p>
        </div>
      </div>

      <div className="pt-2 border-t border-slate-800/80 space-y-1.5 text-xs text-slate-300">
        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-bold">Marks & Features</span>
          <p className="font-medium text-slate-200">{caseData.marks || 'None specified'}</p>
        </div>

        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-bold">Clothing</span>
          <p className="font-medium text-slate-200">{caseData.clothing || 'None specified'}</p>
        </div>

        <div>
          <span className="text-slate-500 block text-[10px] uppercase font-bold">Location & Date</span>
          <p className="font-medium text-slate-200">{caseData.last_seen_found_place}</p>
          <p className="text-[11px] text-slate-400">{new Date(caseData.last_seen_found_time).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}

function SignalBar({ label, score, weight, color }) {
  const pct = Math.round(score * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[11px]">
        <span className="text-slate-300">{label} <span className="text-slate-500">({weight})</span></span>
        <span className="font-mono font-bold text-white">{pct}%</span>
      </div>
      <div className="h-2 w-full bg-slate-950 rounded-full overflow-hidden border border-slate-800">
        <div className={`h-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function intPct(val) {
  return Math.round((val || 0) * 100);
}
