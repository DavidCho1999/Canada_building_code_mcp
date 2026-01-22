'use client';

import { FileText, Plug, Shield, Check } from 'lucide-react';
import { SiAnthropic } from 'react-icons/si';

const steps = [
  {
    step: 1,
    icon: Plug,
    title: 'Connect MCP Server',
    description: 'Add Building Code MCP to Claude Desktop config.',
    color: 'bg-emerald-500',
  },
  {
    step: 2,
    icon: FileText,
    title: 'Bring Your Own PDF',
    description: 'MCP server can help download PDFs, or get them manually from official sources.',
    color: 'bg-blue-500',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 bg-white border-t border-slate-200">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-12">
          <span className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
            How It Works
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            Get Started in 2 Steps
          </h2>
          <p className="text-slate-600 text-sm mb-3">Works with any MCP-compatible client</p>
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

        {/* Steps */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {steps.map((step) => (
            <div key={step.step}>
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200 hover:shadow-lg hover:border-cyan-200 hover:-translate-y-1 transition-all duration-300 h-full">
                <div className="flex items-start gap-4">
                  <div className="relative flex-shrink-0">
                    <div className={`inline-flex items-center justify-center w-12 h-12 ${step.color} text-white rounded-xl`}>
                      <step.icon className="w-6 h-6" />
                    </div>
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-slate-900 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      {step.step}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 mb-1">
                      {step.title}
                    </h3>
                    <p className="text-slate-600 text-sm">
                      {step.description}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Copyright Safe */}
        <div className="bg-slate-50 rounded-2xl p-5 border border-slate-200">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 mb-1">
                Copyright Safe
              </h3>
              <p className="text-slate-600 text-sm mb-2">
                This tool only distributes coordinates (page, position), not the actual text. Content is read from your own PDF files.
              </p>
              <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <Check className="w-3 h-3 text-emerald-500" />
                  No text stored
                </span>
                <span className="flex items-center gap-1">
                  <Check className="w-3 h-3 text-emerald-500" />
                  Your PDF, your content
                </span>
                <span className="flex items-center gap-1">
                  <Check className="w-3 h-3 text-emerald-500" />
                  NRC policy compliant
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
