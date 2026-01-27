'use client';

import { Copy, Check, FileText, Monitor } from 'lucide-react';
import { useState } from 'react';
import { SiAnthropic } from 'react-icons/si';

export default function CTA() {
  const [copiedPip, setCopiedPip] = useState(false);
  const [copiedConfig, setCopiedConfig] = useState(false);

  const pipCommand = 'pip install building-code-mcp';
  const configCode = `{
  "mcpServers": {
    "building-code": {
      "command": "python",
      "args": ["-m", "building_code_mcp"]
    }
  }
}`;

  const copyPipCommand = () => {
    navigator.clipboard.writeText(pipCommand);
    setCopiedPip(true);
    setTimeout(() => setCopiedPip(false), 2000);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(configCode);
    setCopiedConfig(true);
    setTimeout(() => setCopiedConfig(false), 2000);
  };

  return (
    <section id="how-it-works" className="py-20 bg-white border-t border-slate-200">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center">
          <span className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
            One-Time Setup
          </span>
          <h2 className="text-2xl md:text-3xl font-bold mb-4 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            MCP Setup
          </h2>

          {/* Two-column: What You Need (left) + Setup Steps (right) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-10 text-left">
            {/* ── Left: What You Need ── */}
            <div className="flex flex-col gap-4">
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">What You Need</h3>

              {/* Card 1: Building Code PDFs */}
              <div className="rounded-xl border border-slate-200 p-5 hover:border-cyan-200 hover:shadow-lg transition-all duration-300">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-amber-600" />
                  </div>
                  <h3 className="font-bold text-slate-900">Building Code PDFs</h3>
                </div>
                <p className="text-sm text-slate-600 mb-3">
                  Purchase official PDFs from{' '}
                  <button
                    onClick={() => document.getElementById('codes')?.scrollIntoView({ behavior: 'smooth' })}
                    className="text-cyan-600 hover:underline font-medium"
                  >
                    Code Publications
                  </button>
                </p>
                <p className="text-xs text-slate-400">
                  We provide coordinates only. Text is extracted from YOUR local PDF (copyright safe).
                </p>
              </div>

              {/* Card 2: MCP Client */}
              <div className="rounded-xl border border-slate-200 p-5 hover:border-cyan-200 hover:shadow-lg transition-all duration-300">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Monitor className="w-5 h-5 text-blue-600" />
                  </div>
                  <h3 className="font-bold text-slate-900">MCP Client</h3>
                </div>
                <p className="text-sm text-slate-600 mb-3">Any MCP-compatible AI client</p>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-600 rounded-full">
                    <SiAnthropic className="w-3 h-3 text-[#D4A27F]" />
                    Claude Desktop
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-600 rounded-full">
                    <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="18" height="18" rx="2" fill="#000"/><path d="M7 8l4 4-4 4" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/><path d="M13 16h4" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
                    Cursor
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-600 rounded-full">
                    <svg className="w-3 h-3" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="#00D4AA"/><path d="M7 12l3-3v6l-3-3zm7-3l3 3-3 3v-6z" fill="#fff"/></svg>
                    Windsurf
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-slate-100 text-slate-600 rounded-full">
                    <svg className="w-3 h-3" viewBox="0 0 24 24" fill="#007ACC"><path d="M23.15 2.587L18.21.21a1.494 1.494 0 0 0-1.705.29l-9.46 8.63-4.12-3.128a.999.999 0 0 0-1.276.057L.327 7.261A1 1 0 0 0 .326 8.74L3.899 12 .326 15.26a1 1 0 0 0 .001 1.479L1.65 17.94a.999.999 0 0 0 1.276.057l4.12-3.128 9.46 8.63a1.492 1.492 0 0 0 1.704.29l4.942-2.377A1.5 1.5 0 0 0 24 20.06V3.939a1.5 1.5 0 0 0-.85-1.352zm-5.146 14.861L10.826 12l7.178-5.448v10.896z"/></svg>
                    VS Code
                  </span>
                  <a
                    href="https://smithery.ai/server/davidcho/ca-building-code-mcp"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-2 py-1 bg-slate-50 text-slate-400 rounded-full hover:bg-cyan-50 hover:text-cyan-600 transition-all duration-300"
                  >
                    +more
                  </a>
                </div>
              </div>
            </div>

            {/* ── Right: Setup Steps ── */}
            <div className="flex flex-col gap-4">
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Setup Steps</h3>

              <div className="bg-white rounded-xl p-5 border border-slate-200 hover:border-cyan-200 hover:shadow-lg transition-all duration-300">
                {/* Step 1: pip install */}
                <div className="mb-5">
                  <h3 className="text-base font-bold text-slate-900 mb-2">
                    <span className="inline-flex items-center justify-center w-5 h-5 bg-cyan-100 text-cyan-700 rounded-full text-xs font-bold mr-2">1</span>
                    Install
                  </h3>
                  <div className="relative">
                    <div className="bg-slate-900 rounded-lg p-3 font-mono text-sm text-slate-300">
                      pip install building-code-mcp
                    </div>
                    <button
                      onClick={copyPipCommand}
                      className="absolute top-2 right-2 p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-slate-300 transition-colors"
                    >
                      {copiedPip ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Step 2: Add config */}
                <div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">
                    <span className="inline-flex items-center justify-center w-5 h-5 bg-cyan-100 text-cyan-700 rounded-full text-xs font-bold mr-2">2</span>
                    Add to MCP config
                  </h3>
                  <div className="relative">
                    <pre className="bg-slate-900 rounded-lg p-3 font-mono text-xs text-slate-300 overflow-x-auto">
                      {configCode}
                    </pre>
                    <button
                      onClick={copyToClipboard}
                      className="absolute top-2 right-2 p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-slate-300 transition-colors"
                    >
                      {copiedConfig ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
