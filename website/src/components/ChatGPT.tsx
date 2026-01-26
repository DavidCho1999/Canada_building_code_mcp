'use client';

import { motion } from 'framer-motion';
import { MessageSquare, Cpu, ArrowRight, Zap, Users, Code } from 'lucide-react';

const CHATGPT_URL = 'https://chatgpt.com/g/g-6974534ca8e081918b4355f87c6a1f3e-canadian-building-code-navigator';

export default function ChatGPT() {
  return (
    <section id="chatgpt" className="py-20 bg-gradient-to-b from-white to-slate-50">
      <div className="max-w-6xl mx-auto px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-medium border border-blue-200 mb-6">
            <Zap className="w-4 h-4" />
            Two Ways to Access
          </span>
          <h2 className="text-2xl md:text-3xl font-bold mb-4 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            Choose Your Experience
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Same 24,000+ indexed sections, two powerful ways to access them
          </p>
        </motion.div>

        {/* Comparison Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* MCP Server Card - Recommended */}
          <motion.div
            id="mcp-server"
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-8 border border-blue-200 shadow-sm hover:shadow-lg transition-shadow relative overflow-hidden scroll-mt-20"
          >
            <div className="absolute top-4 right-4">
              <span className="px-3 py-1 bg-blue-500 text-white text-xs font-medium rounded-full">
                Recommended
              </span>
            </div>

            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
                <Cpu className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900">MCP Server</h3>
                <p className="text-sm text-slate-500">For Developers</p>
              </div>
            </div>

            <ul className="space-y-3 mb-6">
              <li className="flex items-start gap-3">
                <Code className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">Works with any MCP-compatible client</span>
              </li>
              <li className="flex items-start gap-3">
                <Code className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">Full control over search parameters</span>
              </li>
              <li className="flex items-start gap-3">
                <Code className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">BYOD mode for complete text extraction</span>
              </li>
              <li className="flex items-start gap-3">
                <Code className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">Open source & self-hostable</span>
              </li>
            </ul>

            <button
              onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
              className="inline-flex items-center justify-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-blue-700 hover:scale-105 transition-all duration-300 w-full"
            >
              Setup Instructions
              <ArrowRight className="w-4 h-4" />
            </button>
          </motion.div>

          {/* ChatGPT Card */}
          <motion.div
            id="chatgpt-card"
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm hover:shadow-lg transition-shadow scroll-mt-20"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-emerald-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900">ChatGPT App</h3>
                <p className="text-sm text-slate-500">For Everyone</p>
              </div>
            </div>

            <ul className="space-y-3 mb-6">
              <li className="flex items-start gap-3">
                <Users className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">No setup required - just chat</span>
              </li>
              <li className="flex items-start gap-3">
                <Users className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">Natural conversation interface</span>
              </li>
              <li className="flex items-start gap-3">
                <Users className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">Requires building code PDF for text</span>
              </li>
              <li className="flex items-start gap-3">
                <Users className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                <span className="text-slate-600">Works on mobile & desktop</span>
              </li>
            </ul>

            <a
              href={CHATGPT_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 bg-emerald-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-emerald-700 hover:scale-105 transition-all duration-300 w-full"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.896zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z"/>
              </svg>
              Open in ChatGPT
              <ArrowRight className="w-4 h-4" />
            </a>
          </motion.div>
        </div>

        {/* Technical Comparison Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white rounded-2xl border border-slate-200 overflow-hidden max-w-3xl mx-auto"
        >
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="px-6 py-4 text-left text-base font-medium text-slate-400"></th>
                  <th className="px-6 py-4 text-center text-base font-semibold text-emerald-600">
                    <div className="flex items-center justify-center gap-2">
                      <MessageSquare className="w-5 h-5" />
                      ChatGPT App
                    </div>
                  </th>
                  <th className="px-6 py-4 text-center text-base font-semibold text-blue-600">
                    <div className="flex items-center justify-center gap-2">
                      <Cpu className="w-5 h-5" />
                      MCP Server
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr>
                  <td className="px-6 py-4 text-base text-slate-500">PDF Source</td>
                  <td className="px-6 py-4 text-base text-slate-600 text-center" colSpan={2}>
                    User-provided code PDF
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-base text-slate-500">Speed</td>
                  <td className="px-6 py-4 text-base text-slate-600 text-center">May vary</td>
                  <td className="px-6 py-4 text-base text-blue-600 text-center font-medium">Fast</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-base text-slate-500">Setup</td>
                  <td className="px-6 py-4 text-base text-emerald-600 text-center font-medium">None</td>
                  <td className="px-6 py-4 text-base text-slate-600 text-center">One-time install</td>
                </tr>
                <tr>
                  <td className="px-6 py-4 text-base text-slate-500">Best For</td>
                  <td className="px-6 py-4 text-base text-slate-600 text-center">Casual exploration</td>
                  <td className="px-6 py-4 text-base text-blue-600 text-center font-medium">Production, automation</td>
                </tr>
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
