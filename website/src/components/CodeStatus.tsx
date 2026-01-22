'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';

interface CodeStatusData {
  lastChecked: string;
  hasUpdates: boolean;
  updatedCodes?: string[];
}

export default function CodeStatus() {
  const [status, setStatus] = useState<CodeStatusData | null>(null);

  useEffect(() => {
    fetch('/data/code_status.json')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(() => setStatus(null));
  }, []);

  if (!status) return null;

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-full text-xs text-slate-600">
      {status.hasUpdates ? (
        <>
          <AlertCircle className="w-3 h-3 text-amber-500" />
          <span>Updates available: {status.updatedCodes?.join(', ')}</span>
        </>
      ) : (
        <>
          <CheckCircle className="w-3 h-3 text-emerald-500" />
          <span>All codes up to date</span>
        </>
      )}
      <span className="text-slate-400">|</span>
      <RefreshCw className="w-3 h-3 text-slate-400" />
      <span className="text-slate-400">Checked {status.lastChecked}</span>
    </div>
  );
}
