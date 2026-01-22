'use client';

import { X, Check } from 'lucide-react';

export default function Comparison() {
  return (
    <section className="py-16 bg-gradient-to-b from-slate-50 to-white border-y border-slate-200">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-8">
          <span className="inline-block px-4 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium mb-3">
            No More Hallucinations
          </span>
          <h2 className="text-2xl md:text-3xl font-bold mb-4 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            RAG vs MCP: Building Codes
          </h2>
          <div className="flex flex-wrap justify-center gap-3 text-xs text-emerald-700 mt-4">
            <span>✓ 25,000+ sections indexed</span>
            <span>✓ 100% verifiable</span>
            <span>✓ Exact page numbers</span>
          </div>
        </div>

        {/* Column headers - Desktop only */}
        <div className="hidden md:grid md:grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-red-100 text-red-600 rounded-lg flex items-center justify-center">
              <X className="w-4 h-4" />
            </div>
            <span className="font-semibold text-slate-900">RAG System</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-emerald-100 text-emerald-600 rounded-lg flex items-center justify-center">
              <Check className="w-4 h-4" />
            </div>
            <span className="font-semibold text-slate-900">Building Code MCP</span>
          </div>
        </div>

        {/* Comparison examples */}
        <div className="space-y-3">
          {/* Example 1: Wrong page number */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200">
              {/* RAG - Left */}
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2 md:hidden">
                  <div className="w-5 h-5 bg-red-100 text-red-600 rounded flex items-center justify-center">
                    <X className="w-3 h-3" />
                  </div>
                  <span className="text-xs font-semibold text-slate-700">RAG System</span>
                </div>
                <div className="text-xs text-slate-600 font-mono bg-red-50 px-3 py-2 rounded border border-red-100 mb-2">
                  "Mass timber allowed up to 12 storeys per Section 3.2.2.55, page 200"
                </div>
                <p className="text-xs text-red-700">❌ Wrong page (actual: p.245)</p>
              </div>

              {/* MCP - Right */}
              <div className="p-4 bg-emerald-50/30">
                <div className="flex items-center gap-2 mb-2 md:hidden">
                  <div className="w-5 h-5 bg-emerald-100 text-emerald-600 rounded flex items-center justify-center">
                    <Check className="w-3 h-3" />
                  </div>
                  <span className="text-xs font-semibold text-slate-700">Building Code MCP</span>
                </div>
                <div className="text-xs text-slate-600 font-mono bg-white px-3 py-2 rounded border border-emerald-200 mb-2">
                  "Section 3.2.2.55 found on page 245"
                </div>
                <p className="text-xs text-emerald-700">✓ Exact page verified from PDF</p>
              </div>
            </div>
          </div>

          {/* Example 2: Non-existent section */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200">
              {/* RAG - Left */}
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2 md:hidden">
                  <div className="w-5 h-5 bg-red-100 text-red-600 rounded flex items-center justify-center">
                    <X className="w-3 h-3" />
                  </div>
                  <span className="text-xs font-semibold text-slate-700">RAG System</span>
                </div>
                <div className="text-xs text-slate-600 font-mono bg-red-50 px-3 py-2 rounded border border-red-100 mb-2">
                  "Fire rating between garage and suite is covered in Section 3.2.8.15"
                </div>
                <p className="text-xs text-red-700">❌ Section 3.2.8.15 doesn't exist</p>
              </div>

              {/* MCP - Right */}
              <div className="p-4 bg-emerald-50/30">
                <div className="flex items-center gap-2 mb-2 md:hidden">
                  <div className="w-5 h-5 bg-emerald-100 text-emerald-600 rounded flex items-center justify-center">
                    <Check className="w-3 h-3" />
                  </div>
                  <span className="text-xs font-semibold text-slate-700">Building Code MCP</span>
                </div>
                <div className="text-xs text-slate-600 font-mono bg-white px-3 py-2 rounded border border-emerald-200 mb-2">
                  "Section not found. Did you mean 3.2.1.2?"
                </div>
                <p className="text-xs text-emerald-700">✓ Suggests correct section</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
