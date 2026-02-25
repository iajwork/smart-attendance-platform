import React, { useState, useRef } from 'react';

// --- ICONS ---
const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
);
const FileIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
);
const CalendarIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
);
const UsersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
);
const UserIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
);
const DownloadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
);

// --- MAIN APPLICATION ---
export default function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [reportType, setReportType] = useState('daily'); 
  const [reportScope, setReportScope] = useState('office'); 
  
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));
  const [employeeId, setEmployeeId] = useState('');
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedData, setGeneratedData] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.name.endsWith('.csv') || droppedFile.name.endsWith('.xls') || droppedFile.name.endsWith('.xlsx'))) {
      setFile(droppedFile);
    } else {
      alert("Please upload a valid CSV or Excel file.");
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) setFile(selectedFile);
  };

  const handleGenerate = async () => {
    if (!file) {
      alert("Please upload a data file first.");
      return;
    }
    if (reportScope === 'employee' && !employeeId.trim()) {
      alert("Please enter an Employee ID.");
      return;
    }

    setIsGenerating(true);
    setGeneratedData(null);

    try {
      // 1. Upload File
      const formData = new FormData();
      formData.append('file', file);
      
      const uploadResponse = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData, 
      });

      if (!uploadResponse.ok) throw new Error("File upload failed");

      // 2. Process Data & Fetch Report
      let reportData;
      
      if (reportType === 'daily') {
         // Trigger attendance processing for the specific date
         await fetch(`http://localhost:8000/api/process-attendance?target_date=${selectedDate}`, {
           method: 'POST'
         });
         
         // Fetch the newly generated daily report
         const res = await fetch(`http://localhost:8000/api/reports/daily?target_date=${selectedDate}`);
         reportData = await res.json();
         
      } else {
         // Fetch the monthly report
         const [year, month] = selectedMonth.split('-');
         const res = await fetch(`http://localhost:8000/api/reports/monthly?month=${month}&year=${year}`);
         reportData = await res.json();
      }

      setGeneratedData(reportData);

    } catch (error) {
      console.error("Error generating report:", error);
      alert("Failed to connect to the server or process the report. Ensure backend is running!");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-50 via-slate-50 to-white p-4 md:p-8 font-sans text-slate-800 selection:bg-indigo-200">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* HEADER */}
        <div className="text-center md:text-left mb-10 pt-4">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 bg-clip-text text-transparent pb-2">
            Attendance Insights
          </h1>
          <p className="text-slate-500 mt-2 text-lg font-medium">Transform raw timesheets into beautiful, actionable reports.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* LEFT COLUMN: Configuration */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* 1. File Upload Card */}
            <div className="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100/60 transition-all hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
              <div className="flex items-center gap-3 mb-5">
                <div className="bg-indigo-100 text-indigo-600 p-2 rounded-xl"><FileIcon /></div>
                <h2 className="text-base font-bold text-slate-800">1. Data Source</h2>
              </div>
              
              <div 
                className={`relative overflow-hidden border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 cursor-pointer
                  ${isDragging ? 'border-indigo-500 bg-indigo-50/50 scale-[1.02]' : ''}
                  ${file ? 'border-indigo-400 bg-indigo-50/30' : 'border-slate-300 hover:border-indigo-300 hover:bg-slate-50/50'}`}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleFileDrop}
                onClick={() => fileInputRef.current.click()}
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  className="hidden" 
                  accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                  onChange={handleFileSelect}
                />
                
                {file ? (
                  <div className="flex flex-col items-center text-indigo-700 animate-in zoom-in duration-300">
                    <div className="bg-white p-3 rounded-full shadow-sm mb-3">
                      <FileIcon />
                    </div>
                    <span className="font-bold text-sm truncate w-full px-2">{file.name}</span>
                    <span className="text-xs text-indigo-500/80 mt-1 font-medium bg-indigo-100/50 px-2 py-1 rounded-md">{(file.size / 1024).toFixed(1)} KB</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center text-slate-500">
                    <div className="bg-white p-3 rounded-full shadow-sm mb-3 text-slate-400">
                      <UploadIcon />
                    </div>
                    <span className="font-semibold text-sm">Drag & drop raw data</span>
                    <span className="text-xs text-slate-400 mt-2 font-medium">Supports CSV, XLS, XLSX</span>
                  </div>
                )}
              </div>
            </div>

            {/* 2. Report Configuration Card */}
            <div className="bg-white/70 backdrop-blur-xl p-6 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100/60 transition-all hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
              <div className="flex items-center gap-3 mb-6">
                <div className="bg-violet-100 text-violet-600 p-2 rounded-xl"><CalendarIcon /></div>
                <h2 className="text-base font-bold text-slate-800">2. Report Settings</h2>
              </div>
              
              {/* Type Selection */}
              <div className="mb-6">
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Frequency</label>
                <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={() => setReportType('daily')}
                    className={`flex items-center justify-center gap-2 py-3 rounded-xl border-2 transition-all duration-300 ${reportType === 'daily' ? 'border-transparent bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-200 transform scale-[1.02]' : 'border-slate-200 bg-white text-slate-500 hover:border-indigo-200 hover:bg-indigo-50/30'}`}
                  >
                    <CalendarIcon /> <span className="text-sm font-bold">Daily</span>
                  </button>
                  <button 
                    onClick={() => setReportType('monthly')}
                    className={`flex items-center justify-center gap-2 py-3 rounded-xl border-2 transition-all duration-300 ${reportType === 'monthly' ? 'border-transparent bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-200 transform scale-[1.02]' : 'border-slate-200 bg-white text-slate-500 hover:border-indigo-200 hover:bg-indigo-50/30'}`}
                  >
                    <CalendarIcon /> <span className="text-sm font-bold">Monthly</span>
                  </button>
                </div>
              </div>

              {/* Scope Selection */}
              <div className="mb-6">
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Scope</label>
                <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={() => setReportScope('office')}
                    className={`flex items-center justify-center gap-2 py-3 rounded-xl border-2 transition-all duration-300 ${reportScope === 'office' ? 'border-transparent bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-200 transform scale-[1.02]' : 'border-slate-200 bg-white text-slate-500 hover:border-indigo-200 hover:bg-indigo-50/30'}`}
                  >
                    <UsersIcon /> <span className="text-sm font-bold">Office</span>
                  </button>
                  <button 
                    onClick={() => setReportScope('employee')}
                    className={`flex items-center justify-center gap-2 py-3 rounded-xl border-2 transition-all duration-300 ${reportScope === 'employee' ? 'border-transparent bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-200 transform scale-[1.02]' : 'border-slate-200 bg-white text-slate-500 hover:border-indigo-200 hover:bg-indigo-50/30'}`}
                  >
                    <UserIcon /> <span className="text-sm font-bold">Employee</span>
                  </button>
                </div>
              </div>

              {/* Dynamic Inputs */}
              <div className="space-y-5 pt-5 border-t border-slate-100">
                {reportType === 'daily' ? (
                  <div className="group">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Target Date</label>
                    <input 
                      type="date" 
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm text-slate-700 font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                    />
                  </div>
                ) : (
                  <div className="group">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Target Month</label>
                    <input 
                      type="month" 
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm text-slate-700 font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                      value={selectedMonth}
                      onChange={(e) => setSelectedMonth(e.target.value)}
                    />
                  </div>
                )}

                {reportScope === 'employee' && (
                  <div className="group animate-in fade-in slide-in-from-top-2">
                    <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Employee ID</label>
                    <input 
                      type="text" 
                      placeholder="e.g. EMP-1042"
                      className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-sm text-slate-700 font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all placeholder:text-slate-300"
                      value={employeeId}
                      onChange={(e) => setEmployeeId(e.target.value)}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Action Button */}
            <button 
              onClick={handleGenerate}
              disabled={isGenerating}
              className={`w-full py-4 rounded-2xl font-bold text-white shadow-xl transition-all duration-300 flex justify-center items-center gap-2 overflow-hidden relative
                ${isGenerating 
                  ? 'bg-slate-300 text-slate-500 shadow-none cursor-not-allowed' 
                  : 'bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 hover:shadow-indigo-200 hover:-translate-y-0.5'}`}
            >
              {isGenerating && (
                <div className="absolute inset-0 bg-white/20 w-full animate-[shimmer_1.5s_infinite] -skew-x-12 translate-x-[-100%]" 
                      style={{ backgroundImage: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)' }}></div>
              )}
              {isGenerating ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  Processing...
                </>
              ) : "Generate Magic Report ✨"}
            </button>

          </div>

          {/* RIGHT COLUMN: Results / Preview */}
          <div className="lg:col-span-8">
            <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-slate-100/80 h-full min-h-[600px] flex flex-col overflow-hidden relative">
              
              <div className="h-1.5 w-full bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500 absolute top-0 left-0 right-0"></div>

              {!generatedData ? (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-400 p-8 text-center animate-in fade-in duration-700">
                  <div className="bg-gradient-to-br from-indigo-50 to-violet-50 p-6 rounded-full mb-6 shadow-inner border border-white">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="url(#gradient)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#4f46e5" />
                          <stop offset="100%" stopColor="#8b5cf6" />
                        </linearGradient>
                      </defs>
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-slate-700">Report Canvas</h3>
                  <p className="text-sm mt-3 max-w-xs leading-relaxed">Select your parameters on the left and hit generate to visualize your team's attendance data.</p>
                </div>
              ) : (
                <div className="p-8 flex flex-col h-full animate-in fade-in slide-in-from-bottom-4 duration-500">
                  
                  <div className="flex flex-col md:flex-row md:justify-between md:items-end mb-8 gap-4">
                    <div>
                      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-bold tracking-wide uppercase mb-3">
                        <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                        {generatedData.dateStr}
                      </div>
                      <h3 className="text-2xl font-black text-slate-800 tracking-tight">{generatedData.title}</h3>
                      <p className="text-sm text-slate-500 mt-1 font-medium">{generatedData.subtitle}</p>
                    </div>
                    <div className="flex gap-3">
                      <button className="flex items-center gap-2 px-4 py-2.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl text-sm font-bold hover:bg-emerald-500 hover:text-white transition-all shadow-sm">
                        <DownloadIcon /> Excel
                      </button>
                      <button className="flex items-center gap-2 px-4 py-2.5 bg-rose-50 text-rose-700 border border-rose-200 rounded-xl text-sm font-bold hover:bg-rose-500 hover:text-white transition-all shadow-sm">
                        <DownloadIcon /> PDF
                      </button>
                    </div>
                  </div>

                  <div className="flex-1 overflow-auto rounded-2xl border border-slate-200 shadow-sm bg-white">
                    <table className="w-full text-left border-collapse text-sm whitespace-nowrap">
                      <thead className="bg-slate-50/80 backdrop-blur-md sticky top-0 z-10 shadow-sm">
                        <tr>
                          {generatedData.columns?.map((col, idx) => (
                            <th key={idx} className="px-5 py-4 font-bold text-slate-700 border-b border-slate-200 uppercase tracking-wider text-xs">{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {generatedData.rows?.map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-indigo-50/40 transition-colors group">
                            {Object.values(row).map((val, vIdx) => (
                              <td key={vIdx} className={`px-5 py-3.5 text-slate-600 font-medium ${vIdx === 0 ? 'text-slate-900 font-bold' : ''}`}>
                                {/* BOOLEAN RENDER LOGIC */}
                                {typeof val === 'boolean' ? (
                                  val === true ? (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>Valid
                                    </span>
                                  ) : (
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200">
                                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>Invalid
                                    </span>
                                  )
                                ) : (
                                  val
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div className="mt-5 flex justify-between items-center text-xs font-medium text-slate-400">
                    <div className="flex items-center gap-2">
                      <FileIcon /> Source: <span className="text-slate-600 truncate max-w-[150px]">{file.name}</span>
                    </div>
                    <div className="bg-slate-100 px-3 py-1.5 rounded-lg text-slate-600">
                      Showing <span className="font-bold text-indigo-600">{generatedData.rows?.length || 0}</span> records
                    </div>
                  </div>

                </div>
              )}

            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
