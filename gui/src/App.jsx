import React, { useState, useEffect } from 'react';

function App() {
  const [company, setCompany] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [applyLoading, setApplyLoading] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [resume, setResume] = useState(null);
  const [status, setStatus] = useState({ type: 'info', message: 'Ready' });

  const fetchJobs = async () => {
    try {
      const resp = await fetch('http://127.0.0.1:8000/jobs');
      const data = await resp.json();
      setJobs(data);
    } catch (err) {
      console.error("Failed to fetch jobs", err);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!company) return;
    setSearchLoading(true);
    setStatus({ type: 'info', message: `Searching for jobs at ${company}...` });
    try {
      const resp = await fetch('http://127.0.0.1:8000/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company }),
      });
      const data = await resp.json();
      setStatus({ type: 'success', message: data.result });
      fetchJobs();
    } catch (err) {
      setStatus({ type: 'error', message: 'Search failed' });
    } finally {
      setSearchLoading(false);
    }
  };

  const handleApply = async (e) => {
    e.preventDefault();
    if (!selectedJob) {
      setStatus({ type: 'error', message: 'Please select a job first' });
      return;
    }
    setApplyLoading(true);
    setStatus({ type: 'info', message: `Applying for ${selectedJob.id}...` });
    try {
      const resp = await fetch('http://127.0.0.1:8000/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: selectedJob.id,
          resume_name: resume ? resume.name : 'default_resume.txt'
        }),
      });
      const data = await resp.json();
      setStatus({ type: 'success', message: data.result });
    } catch (err) {
      setStatus({ type: 'error', message: 'Application failed' });
    } finally {
      setApplyLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-8 flex flex-col items-center">
      <header className="w-full max-w-4xl mb-8 flex flex-col items-center gap-2">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-400 to-blue-500 bg-clip-text text-transparent">
          Agentic Job Finder
        </h1>
        <p className="text-slate-400">Search and Apply with A2A Protocol</p>
      </header>

      <main className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Side: Search & Stats */}
        <section className="flex flex-col gap-6">
          <div className="glass p-6 rounded-2xl shadow-xl">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span>🔍</span> Job Search
            </h2>
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                placeholder="Enter company name..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 outline-none"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
              <button
                type="submit"
                disabled={searchLoading}
                className="bg-primary-600 hover:bg-primary-700 active:scale-95 transition-all text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50"
              >
                {searchLoading ? 'Searching...' : 'Search'}
              </button>
            </form>
          </div>

          <div className="glass p-6 rounded-2xl flex-1 flex flex-col overflow-hidden">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span>📋</span> Search Results
            </h2>
            <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
              {jobs.length === 0 ? (
                <p className="text-slate-500 italic text-center py-8">No jobs found yet. Start a search!</p>
              ) : (
                jobs.map((job) => (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${selectedJob?.id === job.id
                        ? 'bg-primary-900/40 border-primary-500/50 scale-[1.02] shadow-lg'
                        : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                      }`}
                  >
                    <h3 className="font-bold text-primary-300">{job.title}</h3>
                    <p className="text-sm text-slate-400 line-clamp-2">{job.description}</p>
                    <div className="mt-2 flex justify-between items-center text-xs">
                      <span className="text-slate-500 font-mono">ID: {job.id}</span>
                      <span className="text-primary-400 bg-primary-950 px-2 py-0.5 rounded-full">{job.company || 'Google'}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        {/* Right Side: Apply & Status */}
        <section className="flex flex-col gap-6">
          <div className="glass p-6 rounded-2xl shadow-xl">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span>🚀</span> Apply for Job
            </h2>
            {selectedJob ? (
              <form onSubmit={handleApply} className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
                <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
                  <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Applying for:</p>
                  <p className="font-semibold text-primary-200">{selectedJob.title}</p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-slate-400">Upload Resume</label>
                  <div className="relative border-2 border-dashed border-slate-800 rounded-xl p-6 flex flex-col items-center gap-2 hover:border-primary-500/50 hover:bg-primary-500/5 transition-all cursor-pointer">
                    <input
                      type="file"
                      className="absolute inset-0 opacity-0 cursor-pointer"
                      onChange={(e) => setResume(e.target.files[0])}
                    />
                    <span>📄</span>
                    <p className="text-sm font-medium">{resume ? resume.name : 'Select resume file'}</p>
                    <p className="text-xs text-slate-500">Click or drag to upload</p>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={applyLoading}
                  className="w-full bg-blue-600 hover:bg-blue-700 active:scale-[0.98] transition-all text-white py-3 rounded-xl font-bold shadow-lg shadow-blue-900/20 disabled:opacity-50"
                >
                  {applyLoading ? 'Processing...' : 'Submit Agent Application'}
                </button>
              </form>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-slate-500 border border-dashed border-slate-800 rounded-xl">
                <span>☝️</span>
                <p>Select a job from the list to apply</p>
              </div>
            )}
          </div>

          <div className="glass p-6 rounded-2xl flex-1">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span>🔔</span> Agent Logs & Status
            </h2>
            <div className={`p-4 rounded-xl border flex gap-3 ${status.type === 'error' ? 'bg-red-950/30 border-red-500/30 text-red-200' :
                status.type === 'success' ? 'bg-green-950/30 border-green-500/30 text-green-200' :
                  'bg-blue-950/30 border-blue-500/30 text-blue-200'
              }`}>
              <div className="text-xl">
                {status.type === 'error' ? '❌' : status.type === 'success' ? '✅' : '💡'}
              </div>
              <div>
                <p className="font-bold text-sm uppercase mb-1">{status.type}</p>
                <p className="text-sm leading-relaxed">{status.message}</p>
              </div>
            </div>

            <div className="mt-6">
              <p className="text-xs text-slate-500 uppercase font-bold mb-3 tracking-widest">A2A Protocol Status</p>
              <div className="space-y-2 text-xs font-mono">
                <div className="flex justify-between items-center p-2 rounded bg-slate-900">
                  <span className="text-slate-400">Search Agent</span>
                  <span className="text-green-500 flex items-center gap-1">● Online</span>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-slate-900">
                  <span className="text-slate-400">Apply Agent</span>
                  <span className="text-green-500 flex items-center gap-1">● Online</span>
                </div>
                <div className="flex justify-between items-center p-2 rounded bg-slate-900 text-slate-500">
                  <span>Discovery Path</span>
                  <span>/.well-known/agent-card.json</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="mt-12 text-slate-600 text-sm">
        Powered by Google ADK & A2A Protocol
      </footer>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      `}</style>
    </div>
  );
}

export default App;
