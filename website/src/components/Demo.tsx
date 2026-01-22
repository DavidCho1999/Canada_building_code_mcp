'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Bot, FileText, ExternalLink } from 'lucide-react';
import clsx from 'clsx';

const demoConversations = [
  {
    id: 'structure',
    category: 'Structural',
    question: 'What is the maximum height for wood buildings in Ontario?',
    answer: 'According to OBC 2024 Section 3.2.2.58, Encapsulated Mass Timber Construction (EMTC) buildings can be up to 12 storeys. Standard wood frame construction is limited to 6 storeys.',
    reference: {
      code: 'OBC Vol.1',
      section: '3.2.2.58',
      page: 245,
    },
  },
  {
    id: 'fire',
    category: 'Fire Safety',
    question: 'When can sprinklers be exempted under NBC?',
    answer: 'Per NBC 2025 Section 3.2.5.12, buildings not more than 3 storeys with a building area not exceeding 2,000m² may be exempt from sprinkler requirements for certain occupancies (Group C, D).',
    reference: {
      code: 'NBC 2025',
      section: '3.2.5.12',
      page: 312,
    },
  },
  {
    id: 'energy',
    category: 'Energy',
    question: 'What is the window U-value requirement in NECB?',
    answer: 'Per NECB 2025 Table 3.2.2.2, for Climate Zone 7A (Toronto, Ottawa), the maximum fenestration U-value is 1.9 W/(m²·K). For Zone 8 (northern regions), it\'s 1.6 W/(m²·K).',
    reference: {
      code: 'NECB 2025',
      section: 'Table 3.2.2.2',
      page: 89,
    },
  },
  {
    id: 'accessibility',
    category: 'Accessibility',
    question: 'What is the maximum ramp slope for barrier-free design?',
    answer: 'Per NBC 2025 Section 3.8.3.4, barrier-free ramps shall have a maximum slope of 1:12 (approximately 8.33%). A level rest area of at least 1.5m × 1.5m is required for every 9m of horizontal run.',
    reference: {
      code: 'NBC 2025',
      section: '3.8.3.4',
      page: 421,
    },
  },
];

export default function Demo() {
  const [activeDemo, setActiveDemo] = useState(demoConversations[0]);

  return (
    <section id="demo" className="py-24 bg-white border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="inline-block px-4 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium mb-4">
            Interactive Demo
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
            See It in Action
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto mb-4">
            Works with any MCP-compatible client.
          </p>
          <div className="flex flex-wrap justify-center gap-3 text-sm">
            <span className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default">Claude Desktop</span>
            <span className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default">Cursor</span>
            <span className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default">Windsurf</span>
            <span className="px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full border border-transparent hover:border-cyan-300 hover:bg-cyan-50 hover:text-cyan-700 transition-all duration-300 cursor-default">VS Code + Copilot</span>
          </div>
        </motion.div>

        {/* Category tabs */}
        <div className="flex flex-wrap justify-center gap-3 mb-8">
          {demoConversations.map((demo) => (
            <button
              key={demo.id}
              onClick={() => setActiveDemo(demo)}
              className={clsx(
                'px-4 py-2 rounded-full text-sm font-medium transition-all duration-300',
                activeDemo.id === demo.id
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 hover:scale-105'
              )}
            >
              {demo.category}
            </button>
          ))}
        </div>

        {/* Chat window */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="max-w-3xl mx-auto"
        >
          <div className="bg-slate-900 rounded-2xl shadow-2xl overflow-hidden">
            {/* Window header */}
            <div className="bg-slate-800 px-4 py-3 flex items-center gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <span className="text-slate-400 text-sm ml-2">Claude Desktop</span>
            </div>

            {/* Chat content */}
            <div className="p-6 space-y-4 min-h-[300px]">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeDemo.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  {/* User message */}
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-tl-none max-w-md">
                      {activeDemo.question}
                    </div>
                  </div>

                  {/* AI response */}
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1 space-y-3">
                      <div className="bg-slate-800 text-slate-100 px-4 py-3 rounded-2xl rounded-tl-none">
                        {activeDemo.answer}
                      </div>

                      {/* Reference card */}
                      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 max-w-sm">
                        <div className="flex items-center gap-2 text-slate-400 text-xs mb-2">
                          <FileText className="w-3 h-3" />
                          Reference
                        </div>
                        <div className="text-slate-200 font-medium mb-1">
                          {activeDemo.reference.code}
                        </div>
                        <div className="text-slate-400 text-sm mb-2">
                          Section {activeDemo.reference.section}
                        </div>
                        <div className="flex items-center gap-2 text-emerald-400 text-sm">
                          <ExternalLink className="w-3 h-3" />
                          Page {activeDemo.reference.page}
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </motion.div>

        {/* Note */}
        <p className="text-center text-slate-500 text-sm mt-6">
          * These are demo examples. Actual responses are based on your PDF files.
        </p>
      </div>
    </section>
  );
}
