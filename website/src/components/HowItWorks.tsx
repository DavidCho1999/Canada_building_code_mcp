'use client';

import { motion } from 'framer-motion';
import { FileText, Plug, Shield, Check } from 'lucide-react';

const steps = [
  {
    step: 1,
    icon: FileText,
    title: 'Bring Your Own PDF',
    description: 'Download Building Code PDFs from official government websites (NRC, Ontario.ca, BC Codes).',
    color: 'bg-blue-500',
  },
  {
    step: 2,
    icon: Plug,
    title: 'Connect MCP Server',
    description: 'Add Building Code MCP to Claude Desktop config. Setup takes 5 minutes.',
    color: 'bg-emerald-500',
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-24 bg-white border-t border-slate-200">
      <div className="max-w-4xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <span className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
            How It Works
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
            Get Started in 2 Steps
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto">
            No complex setup. Anyone can use it.
          </p>
        </motion.div>

        {/* Steps */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {steps.map((step, index) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.15 }}
            >
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
            </motion.div>
          ))}
        </div>

        {/* Copyright Safe */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-slate-50 rounded-2xl p-5 border border-slate-200"
        >
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
              <div className="flex flex-wrap gap-4 text-xs text-slate-500">
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
        </motion.div>
      </div>
    </section>
  );
}
