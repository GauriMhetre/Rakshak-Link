import React, { useState } from 'react';
import { UserPlus, Camera, MapPin, Calendar, Phone, ShieldAlert, Sparkles, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

export default function IntakeForm({ role, district, onCaseCreated, setActiveTab }) {
  const [formData, setFormData] = useState({
    type: 'MISSING',
    name: '',
    devanagari_name: '',
    aliases: '',
    age: 14,
    sex: 'MALE',
    height_cm: 155,
    marks: '',
    clothing: '',
    language: 'Marathi',
    last_seen_found_place: '',
    last_seen_found_time: new Date().toISOString().slice(0, 16),
    district: district || 'Pune',
    phone_numbers: '',
    photo_url: '',
  });

  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMsg('');
    setErrorMsg('');

    try {
      const payload = {
        ...formData,
        age: parseInt(formData.age, 10),
        height_cm: parseFloat(formData.height_cm),
        aliases: formData.aliases ? formData.aliases.split(',').map(s => s.trim()) : [],
        phone_numbers: formData.phone_numbers ? formData.phone_numbers.split(',').map(s => s.trim()) : [],
        latitude: formData.district === 'Pune' ? 18.5204 : formData.district === 'Thane' ? 19.2183 : formData.district === 'Mumbai Suburban' ? 19.0760 : 21.1458,
        longitude: formData.district === 'Pune' ? 73.8567 : formData.district === 'Thane' ? 72.9781 : formData.district === 'Mumbai Suburban' ? 72.8777 : 79.0882,
        last_seen_found_time: new Date(formData.last_seen_found_time).toISOString(),
      };

      const created = await api.createCase(payload, role, district);
      setSuccessMsg(`Case ${created.case_number} registered! Multi-signal cross-district matching engine activated.`);
      if (onCaseCreated) onCaseCreated(created);
      
      setTimeout(() => {
        setActiveTab('matches');
      }, 1500);

    } catch (err) {
      setErrorMsg(err.message || 'Failed to submit case report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-6">
      <div className="glass-card p-6 md:p-8">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6 pb-4 border-b border-earth/20">
          <div className="p-3 bg-amber-500/10 text-earth rounded-xl border border-amber-500/20">
            <UserPlus className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-ashgray">Official Case Intake Report</h2>
            <p className="text-xs text-ashgray/70">Register Missing or Found/Rescued individual to trigger automated cross-district match engine</p>
          </div>
        </div>

        {successMsg && (
          <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 rounded-xl flex items-center space-x-3 text-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <p className="font-semibold">{successMsg}</p>
              <p className="text-xs opacity-80">Redirecting to candidate Match Review...</p>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl flex items-center space-x-3 text-sm">
            <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
            <p>{errorMsg}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Case Type Toggle */}
          <div className="grid grid-cols-2 gap-4 p-1 bg-darkblue/40 rounded-xl border border-earth/20">
            <button
              type="button"
              onClick={() => setFormData(p => ({ ...p, type: 'MISSING' }))}
              className={`py-3 rounded-lg text-sm font-bold flex items-center justify-center space-x-2 transition-all ${
                formData.type === 'MISSING'
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-lg'
                  : 'text-ashgray/70 hover:text-ashgray'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-rose-400 animate-pulse" />
              <span>MISSING PERSON REPORT</span>
            </button>

            <button
              type="button"
              onClick={() => setFormData(p => ({ ...p, type: 'FOUND' }))}
              className={`py-3 rounded-lg text-sm font-bold flex items-center justify-center space-x-2 transition-all ${
                formData.type === 'FOUND'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-lg'
                  : 'text-ashgray/70 hover:text-ashgray'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>FOUND / RESCUED INDIVIDUAL</span>
            </button>
          </div>

          {/* Personal Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Full Name (English) *</label>
              <input
                type="text"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g. Ramesh Sharma"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Devanagari Name (हिंदी / मराठी)</label>
              <input
                type="text"
                name="devanagari_name"
                value={formData.devanagari_name}
                onChange={handleChange}
                placeholder="e.g. रमेश शर्मा"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Aliases / Known Nicknames (comma separated)</label>
              <input
                type="text"
                name="aliases"
                value={formData.aliases}
                onChange={handleChange}
                placeholder="e.g. Ramu, Chhotu"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-xs font-semibold text-ashgray mb-1">Age *</label>
                <input
                  type="number"
                  name="age"
                  required
                  min="0"
                  max="120"
                  value={formData.age}
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-ashgray mb-1">Sex *</label>
                <select
                  name="sex"
                  value={formData.sex}
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
                >
                  <option value="MALE">MALE</option>
                  <option value="FEMALE">FEMALE</option>
                  <option value="OTHER">OTHER</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-ashgray mb-1">Height (cm)</label>
                <input
                  type="number"
                  name="height_cm"
                  value={formData.height_cm}
                  onChange={handleChange}
                  className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Physical Attributes & Identifiers */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Distinguishing Marks / Scars / Tattoos</label>
              <textarea
                name="marks"
                rows="2"
                value={formData.marks}
                onChange={handleChange}
                placeholder="e.g. Mole on left cheek, burn mark on right wrist"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Clothing Details</label>
              <textarea
                name="clothing"
                rows="2"
                value={formData.clothing}
                onChange={handleChange}
                placeholder="e.g. Blue denim trousers, light yellow top"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Location, Time & Contact */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">District *</label>
              <select
                name="district"
                value={formData.district}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              >
                <option value="Pune">Pune</option>
                <option value="Mumbai Suburban">Mumbai Suburban</option>
                <option value="Thane">Thane</option>
                <option value="Nagpur">Nagpur</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Last Seen / Found Location *</label>
              <input
                type="text"
                name="last_seen_found_place"
                required
                value={formData.last_seen_found_place}
                onChange={handleChange}
                placeholder="e.g. Shivajinagar Bus Stand, Pune"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Date & Time *</label>
              <input
                type="datetime-local"
                name="last_seen_found_time"
                required
                value={formData.last_seen_found_time}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Associated Phone Numbers (comma separated)</label>
              <input
                type="text"
                name="phone_numbers"
                value={formData.phone_numbers}
                onChange={handleChange}
                placeholder="e.g. +919820012345, +919820099999"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-ashgray mb-1">Photo URL (Optional)</label>
              <input
                type="text"
                name="photo_url"
                value={formData.photo_url}
                onChange={handleChange}
                placeholder="https://... or leave blank for auto synthetic embedding"
                className="w-full px-3 py-2 bg-darkblue/40 border border-earth/20 rounded-lg text-sm text-slate-100 focus:border-amber-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Privacy Disclaimer */}
          <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg text-xs text-amber-300/80 flex items-start space-x-2">
            <Sparkles className="w-4 h-4 text-earth shrink-0 mt-0.5" />
            <p>
              <strong>Privacy-Preserving Cross-District Policy:</strong> Photo vector embeddings are extracted locally and shared cross-district for scoring. Raw photos remain restricted to the originating district until a link is formally verified by an Investigating Officer.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-slate-950 font-bold rounded-xl shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center space-x-2"
          >
            {loading ? (
              <span>Extracting Embeddings & Searching Matches...</span>
            ) : (
              <>
                <UserPlus className="w-5 h-5 stroke-[2.5]" />
                <span>Submit Intake & Search Cross-District Matches</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
