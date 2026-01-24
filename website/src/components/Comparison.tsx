'use client';

import { X, Check, Shield, AlertTriangle, FileCheck } from 'lucide-react';

export default function Comparison() {
  return (
    <section className="py-16 bg-gradient-to-b from-slate-50 to-white border-y border-slate-200">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-8">
          <span className="inline-block px-4 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium mb-3">
            Sound Familiar?
          </span>
          <h2 className="text-2xl md:text-3xl font-bold mb-4 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            When AI Gets Building Codes Wrong
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto">
            AI often <span className="font-semibold text-slate-800">hallucinates page numbers</span> and invents <span className="font-semibold text-slate-800">non-existent sections</span>
          </p>
        </div>

        {/* Column headers - Desktop only */}
        <div className="hidden md:grid md:grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 text-orange-600 rounded-xl flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <span className="font-bold text-slate-900">Generic AI</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center">
              <FileCheck className="w-5 h-5" />
            </div>
            <span className="font-bold text-slate-900">Building Code Navigator</span>
          </div>
        </div>

        {/* Comparison examples */}
        <div className="space-y-3">
          {/* Example 1: Wrong page number */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200">
              {/* RAG - Left */}
              <div className="p-5">
                <div className="flex items-center gap-2 mb-3 md:hidden">
                  <div className="w-6 h-6 bg-orange-100 text-orange-600 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-semibold text-slate-700">Generic AI</span>
                </div>
                <p className="text-xs text-orange-600 font-medium mb-2">Wrong Page Number</p>
                <div className="text-sm text-slate-600 font-mono bg-orange-50 px-3 py-2 rounded border border-orange-200 mb-2">
                  "Mass timber allowed up to 12 storeys per Section 3.2.2.55, page 200"
                </div>
                <p className="text-sm text-orange-700 font-medium">❌ Wrong page (actual: p.245)</p>
              </div>

              {/* MCP - Right */}
              <div className="p-5 bg-blue-50/30">
                <div className="flex items-center gap-2 mb-3 md:hidden">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center">
                    <FileCheck className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-semibold text-slate-700">Building Code Navigator</span>
                </div>
                <p className="text-xs text-blue-600 font-medium mb-2">Exact Page Verified</p>
                <div className="text-sm text-slate-600 font-mono bg-white px-3 py-2 rounded border border-blue-200 mb-2">
                  "Section 3.2.2.55 found on page 245"
                </div>
                <p className="text-sm text-blue-700 font-medium">✓ Exact page verified from PDF</p>
              </div>
            </div>
          </div>

          {/* Example 2: Non-existent section */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200">
              {/* RAG - Left */}
              <div className="p-5">
                <div className="flex items-center gap-2 mb-3 md:hidden">
                  <div className="w-6 h-6 bg-orange-100 text-orange-600 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-semibold text-slate-700">Generic AI</span>
                </div>
                <p className="text-xs text-orange-600 font-medium mb-2">Non-existent Section</p>
                <div className="text-sm text-slate-600 font-mono bg-orange-50 px-3 py-2 rounded border border-orange-200 mb-2">
                  "Fire rating between garage and suite is covered in Section 3.2.8.15"
                </div>
                <p className="text-sm text-orange-700 font-medium">❌ Section 3.2.8.15 doesn't exist</p>
              </div>

              {/* MCP - Right */}
              <div className="p-5 bg-blue-50/30">
                <div className="flex items-center gap-2 mb-3 md:hidden">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center">
                    <FileCheck className="w-4 h-4" />
                  </div>
                  <span className="text-sm font-semibold text-slate-700">Building Code Navigator</span>
                </div>
                <p className="text-xs text-blue-600 font-medium mb-2">Smart Suggestions</p>
                <div className="text-sm text-slate-600 font-mono bg-white px-3 py-2 rounded border border-blue-200 mb-2">
                  "Section not found. Did you mean 3.2.1.2?"
                </div>
                <p className="text-sm text-blue-700 font-medium">✓ Suggests correct section</p>
              </div>
            </div>
          </div>
        </div>

        {/* Copyright Safe */}
        <div className="mt-10 bg-emerald-50 rounded-2xl p-8 border border-emerald-200">
          <div className="flex items-center gap-5">
            <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <Shield className="w-7 h-7" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">Copyright Safe</h4>
              <p className="text-base text-slate-600">
                Only coordinates distributed, not actual text.<br className="hidden md:block" />
                Content read from your own PDF.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
