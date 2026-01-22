'use client';

import { ArrowRight, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { SiAnthropic } from 'react-icons/si';

export default function CTA() {
  const [copied, setCopied] = useState(false);

  const configCode = `{
  "mcpServers": {
    "building-code": {
      "command": "uvx",
      "args": ["building-code-mcp"]
    }
  }
}`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(configCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="setup" className="py-20 bg-white border-t border-slate-200">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center">
          <span className="inline-block px-4 py-1 bg-cyan-100 text-cyan-700 rounded-full text-sm font-medium mb-4">
            Get Started
          </span>
          <h2 className="text-2xl md:text-3xl font-bold mb-8 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            Quick Setup
          </h2>

          {/* Installation Options */}
          <div className="grid md:grid-cols-2 gap-4 mb-10 text-left">
            {/* Option 1: pip install */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 hover:border-cyan-200 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  1
                </div>
                <h3 className="font-semibold text-slate-900">pip install</h3>
              </div>
              <div className="bg-slate-900 rounded-lg p-3 font-mono text-sm text-slate-300 mb-4">
                pip install building-code-mcp
              </div>
              <p className="text-xs text-slate-500 mb-2">
                Add this to your MCP client config file:
              </p>
              <div className="relative">
                <pre className="bg-slate-900 rounded-lg p-3 font-mono text-xs text-slate-300 overflow-x-auto">
                  {configCode}
                </pre>
                <button
                  onClick={copyToClipboard}
                  className="absolute top-2 right-2 p-1.5 bg-slate-700 hover:bg-slate-600 rounded text-slate-300 transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {/* Option 2: Smithery */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 hover:border-cyan-200 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-6 h-6 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  2
                </div>
                <h3 className="font-semibold text-slate-900">Smithery (One-click)</h3>
              </div>
              <a
                href="https://smithery.ai/server/davidcho/ca-building-code-mcp"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-slate-900 text-white px-4 py-3 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors w-full justify-center mb-3"
              >
                Install on Smithery
                <ArrowRight className="w-4 h-4" />
              </a>
              <p className="text-xs text-slate-500">No manual config needed. Just click and install.</p>
            </div>
          </div>

          {/* MCP Clients */}
          <div className="text-center mt-8">
            <p className="text-slate-600 text-sm mb-3">Works with <span className="font-semibold">any MCP-compatible client</span></p>
            <div className="flex gap-3 text-sm justify-center flex-wrap">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default whitespace-nowrap">
                <SiAnthropic className="w-4 h-4 text-[#D4A27F]" />
                Claude Desktop
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default whitespace-nowrap">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="18" height="18" rx="2" fill="#000"/><path d="M7 8l4 4-4 4" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/><path d="M13 16h4" stroke="#fff" strokeWidth="2" strokeLinecap="round"/></svg>
                Cursor
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default whitespace-nowrap">
                <svg className="w-4 h-4" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="#00D4AA"/><path d="M7 12l3-3v6l-3-3zm7-3l3 3-3 3v-6z" fill="#fff"/></svg>
                Windsurf
              </span>
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default whitespace-nowrap">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="#007ACC"><path d="M23.15 2.587L18.21.21a1.494 1.494 0 0 0-1.705.29l-9.46 8.63-4.12-3.128a.999.999 0 0 0-1.276.057L.327 7.261A1 1 0 0 0 .326 8.74L3.899 12 .326 15.26a1 1 0 0 0 .001 1.479L1.65 17.94a.999.999 0 0 0 1.276.057l4.12-3.128 9.46 8.63a1.492 1.492 0 0 0 1.704.29l4.942-2.377A1.5 1.5 0 0 0 24 20.06V3.939a1.5 1.5 0 0 0-.85-1.352zm-5.146 14.861L10.826 12l7.178-5.448v10.896z"/></svg>
                VS Code
              </span>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
