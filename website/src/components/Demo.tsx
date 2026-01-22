'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Bot, FileText, ExternalLink } from 'lucide-react';
import clsx from 'clsx';

const demoConversations = [
  {
    id: 'mass-timber',
    category: 'Mass Timber',
    question: 'Can I build a 10-storey condo with mass timber in Toronto?',
    answer: 'Yes! OBC 2024 now permits Encapsulated Mass Timber Construction (EMTC) up to 12 storeys. Your 10-storey condo qualifies. Key requirements: noncombustible protection on mass timber elements, 2-hour fire separation between suites, and automatic sprinklers throughout.',
    reference: {
      code: 'OBC Vol.1',
      section: '3.2.2.58',
      page: 245,
    },
  },
  {
    id: 'egress',
    category: 'Egress',
    question: 'My client wants a single exit stair for a 3-storey office. Possible?',
    answer: 'Under NBC 2025, a single exit is permitted if: floor area ≤ 200m² per storey, travel distance ≤ 15m to exit, and building is sprinklered. However, for a typical office building exceeding these limits, you\'ll need minimum 2 exits with separation ≥ 9m or half the diagonal.',
    reference: {
      code: 'NBC 2025',
      section: '3.4.2.1',
      page: 287,
    },
  },
  {
    id: 'energy',
    category: 'NECB',
    question: 'What\'s the required wall insulation for a new building in Ottawa?',
    answer: 'Ottawa is Climate Zone 6. Per NECB 2020, above-grade walls require minimum R-27.4 (RSI 4.84) for mass walls or R-24.5 (RSI 4.31) for steel-framed. The 2025 NECB increases this by ~15%. Consider continuous exterior insulation to minimize thermal bridging.',
    reference: {
      code: 'NECB 2020',
      section: 'Table 3.2.2.2',
      page: 89,
    },
  },
  {
    id: 'fire-rating',
    category: 'Fire Rating',
    question: 'What fire rating do I need between a parking garage and residential above?',
    answer: 'Per OBC 3.2.1.2, a parking garage (Group F3) below residential (Group C) requires a 2-hour fire separation. If the garage is sprinklered and ≤ 2 storeys below grade, the floor assembly above must be a fire separation with no openings except for required exits.',
    reference: {
      code: 'OBC Vol.1',
      section: '3.2.1.2',
      page: 156,
    },
  },
];

export default function Demo() {
  const [activeDemo, setActiveDemo] = useState(demoConversations[0]);

  return (
    <section id="demo" className="py-24 bg-white border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            See It in Action
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto">
            Real examples of building code queries.
          </p>
        </div>

        {/* Category tabs */}
        <div className="flex gap-3 mb-8 overflow-x-auto md:flex-wrap md:justify-center md:overflow-visible scrollbar-hide">
          {demoConversations.map((demo) => (
            <button
              key={demo.id}
              onClick={() => setActiveDemo(demo)}
              className={clsx(
                'px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 whitespace-nowrap',
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
        <div className="max-w-3xl mx-auto">
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
            <div className="p-4 md:p-6 space-y-4 min-h-[280px] md:min-h-[300px]">
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
                  <div className="flex items-start gap-2 md:gap-3">
                    <div className="w-7 h-7 md:w-8 md:h-8 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="w-3.5 h-3.5 md:w-4 md:h-4 text-white" />
                    </div>
                    <div className="bg-blue-600 text-white px-3 md:px-4 py-2 md:py-3 rounded-2xl rounded-tl-none text-sm md:text-base">
                      {activeDemo.question}
                    </div>
                  </div>

                  {/* AI response */}
                  <div className="flex items-start gap-2 md:gap-3">
                    <div className="w-7 h-7 md:w-8 md:h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Bot className="w-3.5 h-3.5 md:w-4 md:h-4 text-white" />
                    </div>
                    <div className="flex-1 space-y-3">
                      <div className="bg-slate-800 text-slate-100 px-3 md:px-4 py-2 md:py-3 rounded-2xl rounded-tl-none text-sm md:text-base">
                        {activeDemo.answer}
                      </div>

                      {/* Reference card */}
                      <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-3 md:p-4 max-w-xs md:max-w-sm">
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
        </div>

        {/* Note */}
        <p className="text-center text-slate-500 text-sm mt-6">
          * These are demo examples. Actual responses are based on your PDF files.
        </p>
      </div>
    </section>
  );
}
