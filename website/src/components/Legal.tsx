'use client';

import { motion } from 'framer-motion';
import { Shield, Check } from 'lucide-react';

export default function Legal() {
  return (
    <section className="py-16 bg-white border-t border-slate-200">
      <div className="max-w-3xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-2xl p-6 border border-slate-200"
        >
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">
                Copyright Safe
              </h3>
              <p className="text-slate-600 text-sm mb-3">
                This tool only distributes coordinates (page, position), not the actual text.
                Content is read from your own PDF files.
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
