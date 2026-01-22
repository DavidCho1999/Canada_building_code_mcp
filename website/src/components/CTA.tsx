'use client';

import { ArrowRight, Copy, Check } from 'lucide-react';
import { useState } from 'react';

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

        </div>
      </div>
    </section>
  );
}
