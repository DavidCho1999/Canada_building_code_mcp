'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, ArrowRight } from 'lucide-react';

const typewriterQueries = [
  'What is the minimum stair width in Ontario?',
  'NBC 2025 fire rating requirements',
  'BCBC maximum height for wood buildings',
  'Energy code window U-value requirements',
  'Barrier-free ramp slope limits',
];

export default function Hero() {
  const [currentQuery, setCurrentQuery] = useState('');
  const [queryIndex, setQueryIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const query = typewriterQueries[queryIndex];

    const timeout = setTimeout(() => {
      if (!isDeleting) {
        if (currentQuery.length < query.length) {
          setCurrentQuery(query.slice(0, currentQuery.length + 1));
        } else {
          setTimeout(() => setIsDeleting(true), 2000);
        }
      } else {
        if (currentQuery.length > 0) {
          setCurrentQuery(currentQuery.slice(0, -1));
        } else {
          setIsDeleting(false);
          setQueryIndex((prev) => (prev + 1) % typewriterQueries.length);
        }
      }
    }, isDeleting ? 30 : 80);

    return () => clearTimeout(timeout);
  }, [currentQuery, isDeleting, queryIndex]);

  return (
    <section className="relative min-h-[85vh] md:min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-slate-50 to-white">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-100 rounded-full blur-3xl opacity-50" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-100 rounded-full blur-3xl opacity-50" />
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-6 py-12 md:py-20 text-center">
        {/* Badges */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-wrap justify-center gap-3 mb-4 md:mb-8"
        >
          <span className="inline-flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 bg-blue-50 text-blue-700 rounded-full text-xs md:text-sm font-medium border border-blue-200">
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            25,707 sections indexed
          </span>
          <span className="inline-flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 bg-emerald-50 text-emerald-700 rounded-full text-xs md:text-sm font-medium border border-emerald-200">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            Free & Open Source
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-4xl md:text-6xl font-bold text-slate-900 mb-6 leading-tight"
        >
          Canadian Building Codes
          <br />
          <span className="bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">MCP Server</span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-lg md:text-xl text-slate-600 mb-6 md:mb-12 max-w-2xl mx-auto"
        >
          Search 14 codes and 25,707 sections in plain language.
          <br className="hidden md:block" />
          No more hunting through PDFs. Just ask.
        </motion.p>

        {/* Fake Search Bar with Typewriter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="max-w-2xl mx-auto mb-6 md:mb-12"
        >
          <div className="relative bg-white rounded-2xl shadow-xl border border-slate-200 p-2">
            <div className="flex items-center gap-3 px-3 md:px-4 py-3 pr-12 md:pr-24">
              <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
              <span className="text-slate-700 text-left flex-1 text-sm md:text-base truncate">
                {currentQuery}
                <span className="inline-block w-0.5 h-4 bg-blue-600 ml-1 animate-pulse -mb-0.5" />
              </span>
            </div>
            <div className="absolute right-2 md:right-4 top-1/2 -translate-y-1/2">
              <div className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-3 md:px-4 py-2 rounded-xl text-xs md:text-sm font-medium">
                Search
              </div>
            </div>
          </div>
        </motion.div>

        {/* CTA Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <a
            href="#how-it-works"
            className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-8 py-4 rounded-xl font-medium hover:scale-105 hover:shadow-xl hover:shadow-cyan-500/30 transition-all duration-300"
          >
            Get Started
            <ArrowRight className="w-4 h-4" />
          </a>
        </motion.div>
      </div>

          </section>
  );
}
