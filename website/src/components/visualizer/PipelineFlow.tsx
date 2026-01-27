'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import {
  User,
  Server,
  Scissors,
  RefreshCw,
  BarChart3,
  BookOpen,
  CheckCircle2,
  FileText,
  Sparkles,
} from 'lucide-react';
import type { MetadataSummary } from '@/types/visualizer';

// ── Animation Variants ──────────────────────────────
const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12, delayChildren: 0.3 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

// ── FlowNode ────────────────────────────────────────
// Glassmorphic card with colored glow
function FlowNode({
  icon: Icon,
  label,
  sublabel,
  badges,
  color,
  large,
  vertical,
}: {
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  label: string;
  sublabel?: string;
  badges?: string[];
  color: string;
  large?: boolean;
  vertical?: boolean;
}) {
  return (
    <motion.div
      variants={fadeUp}
      className={`relative rounded-2xl border backdrop-blur-xl shrink-0 ${
        large ? 'px-8 py-6' : vertical ? 'px-4 py-4' : 'px-6 py-4'
      }`}
      style={{
        backgroundColor: `${color}0a`,
        borderColor: `${color}33`,
        boxShadow: `0 0 40px ${color}15`,
      }}
    >
      {/* Pulse ring */}
      <motion.div
        className="absolute inset-0 rounded-2xl border pointer-events-none"
        style={{ borderColor: color }}
        animate={{ opacity: [0.15, 0.04, 0.15] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />

      {vertical ? (
        /* ── Vertical: icon top, text below, centered ── */
        <div className="relative flex flex-col items-center gap-2 text-center">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ backgroundColor: `${color}15` }}
          >
            <Icon className="w-5 h-5" style={{ color }} />
          </div>
          <div>
            <h3 className="font-semibold text-sm text-white leading-tight">{label}</h3>
            {sublabel && (
              <p className="text-slate-400 text-xs mt-0.5">{sublabel}</p>
            )}
          </div>
          {badges && badges.length > 0 && (
            <div className="flex flex-wrap justify-center gap-1.5">
              {badges.map((b) => (
                <span
                  key={b}
                  className="text-[10px] font-medium px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: `${color}15`, color }}
                >
                  {b}
                </span>
              ))}
            </div>
          )}
        </div>
      ) : (
        /* ── Horizontal: icon left, text right ── */
        <>
          <div className="relative flex items-center gap-3">
            <div
              className={`${
                large ? 'w-12 h-12' : 'w-10 h-10'
              } rounded-xl flex items-center justify-center shrink-0`}
              style={{ backgroundColor: `${color}15` }}
            >
              <Icon
                className={large ? 'w-6 h-6' : 'w-5 h-5'}
                style={{ color }}
              />
            </div>
            <div>
              <h3
                className={`font-semibold ${
                  large ? 'text-xl' : 'text-base'
                } text-white`}
              >
                {label}
              </h3>
              {sublabel && (
                <p className="text-slate-400 text-sm mt-0.5">{sublabel}</p>
              )}
            </div>
          </div>

          {badges && badges.length > 0 && (
            <div className="relative flex flex-wrap gap-2 mt-3">
              {badges.map((b) => (
                <span
                  key={b}
                  className="text-xs font-medium px-2.5 py-1 rounded-full"
                  style={{ backgroundColor: `${color}15`, color }}
                >
                  {b}
                </span>
              ))}
            </div>
          )}
        </>
      )}
    </motion.div>
  );
}

// ── Connector (vertical line + flowing dots) ────────
function Connector({
  color,
  height = 48,
}: {
  color: string;
  height?: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      className="flex justify-center"
      style={{ height }}
    >
      <div
        className="relative w-px h-full"
        style={{ backgroundColor: `${color}33` }}
      >
        <motion.div
          className="absolute left-1/2 -translate-x-1/2 w-2 h-2 rounded-full"
          style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }}
          animate={{
            top: ['-4px', `${height - 4}px`],
            opacity: [0, 1, 1, 0],
          }}
          transition={{
            duration: 1.8,
            repeat: Infinity,
            ease: 'linear',
            times: [0, 0.15, 0.85, 1],
          }}
        />
        <motion.div
          className="absolute left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full"
          style={{
            backgroundColor: color,
            boxShadow: `0 0 6px ${color}`,
          }}
          animate={{
            top: ['-4px', `${height - 4}px`],
            opacity: [0, 0.6, 0.6, 0],
          }}
          transition={{
            duration: 1.8,
            repeat: Infinity,
            ease: 'linear',
            delay: 0.9,
            times: [0, 0.15, 0.85, 1],
          }}
        />
      </div>
    </motion.div>
  );
}

// ── Fan-out SVG (1 → 3) ────────────────────────────
function FanOut({ color }: { color: string }) {
  return (
    <motion.div variants={fadeUp} className="flex justify-center">
      <svg
        width="300"
        height="24"
        viewBox="0 0 300 24"
        fill="none"
        className="overflow-visible"
      >
        <path d="M150 0 Q150 12 50 24" stroke={color} strokeOpacity="0.25" strokeWidth="1" />
        <line x1="150" y1="0" x2="150" y2="24" stroke={color} strokeOpacity="0.25" strokeWidth="1" />
        <path d="M150 0 Q150 12 250 24" stroke={color} strokeOpacity="0.25" strokeWidth="1" />
        <circle cx="50" cy="24" r="2" fill={color} fillOpacity="0.35" />
        <circle cx="150" cy="24" r="2" fill={color} fillOpacity="0.35" />
        <circle cx="250" cy="24" r="2" fill={color} fillOpacity="0.35" />
      </svg>
    </motion.div>
  );
}

// ── Fan-in SVG (3 → 1) ─────────────────────────────
function FanIn({ color }: { color: string }) {
  return (
    <motion.div variants={fadeUp} className="flex justify-center">
      <svg
        width="300"
        height="24"
        viewBox="0 0 300 24"
        fill="none"
        className="overflow-visible"
      >
        <path d="M50 0 Q50 12 150 24" stroke={color} strokeOpacity="0.25" strokeWidth="1" />
        <line x1="150" y1="0" x2="150" y2="24" stroke={color} strokeOpacity="0.25" strokeWidth="1" />
        <path d="M250 0 Q250 12 150 24" stroke={color} strokeOpacity="0.25" strokeWidth="1" />
        <circle cx="150" cy="24" r="2" fill={color} fillOpacity="0.35" />
      </svg>
    </motion.div>
  );
}

// ── Horizontal Connector (left→right line + flowing dot) ─
function HConnector({
  color,
  width = 40,
}: {
  color: string;
  width?: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      className="flex items-center shrink-0"
      style={{ width }}
    >
      <div
        className="relative h-px w-full"
        style={{ backgroundColor: `${color}33` }}
      >
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full"
          style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }}
          animate={{
            left: ['-4px', `${width - 4}px`],
            opacity: [0, 1, 1, 0],
          }}
          transition={{
            duration: 1.8,
            repeat: Infinity,
            ease: 'linear',
            times: [0, 0.15, 0.85, 1],
          }}
        />
      </div>
    </motion.div>
  );
}

// ── Processing Step (compact pill) ──────────────────
function ProcessStep({
  icon: Icon,
  label,
  sublabel,
  color,
}: {
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  label: string;
  sublabel: string;
  color: string;
}) {
  return (
    <div
      className="flex flex-col items-center gap-1.5 px-4 py-3 rounded-xl border backdrop-blur-xl"
      style={{
        backgroundColor: `${color}0a`,
        borderColor: `${color}26`,
      }}
    >
      <Icon className="w-4 h-4" style={{ color }} />
      <span className="text-sm font-medium text-white">{label}</span>
      <span className="text-xs text-slate-400">{sublabel}</span>
    </div>
  );
}

// ═════════════════════════════════════════════════════
// ██ MAIN: PipelineFlow ██
// ═════════════════════════════════════════════════════

export default function PipelineFlow() {
  const [metadata, setMetadata] = useState<MetadataSummary | null>(null);

  useEffect(() => {
    fetch('/visualizer/metadata-summary.json')
      .then((r) => r.json())
      .then(setMetadata)
      .catch(console.error);
  }, []);

  return (
    <section id="pipeline" className="bg-slate-950 py-16 md:py-24">
      {/* ── Section Header ── */}
      <div className="text-center mb-10 md:mb-14 px-6">
        <span className="inline-block px-4 py-1 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-medium mb-4 border border-cyan-500/20">
          Under the Hood
        </span>
        <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">
          How MCP Processes a Query
        </h2>
        <p className="text-slate-400 max-w-lg mx-auto text-sm">
          From question to exact section — the full pipeline at a glance
        </p>
      </div>

      {/* ── Mobile: Vertical Pipeline ── */}
      <motion.div
        className="md:hidden max-w-2xl mx-auto px-6 flex flex-col items-center"
        variants={stagger}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.1 }}
      >
        <FlowNode
          icon={User}
          label="User / Claude"
          sublabel={'"What are the fire rating requirements?"'}
          color="#3b82f6"
        />
        <Connector color="#3b82f6" height={28} />
        <FlowNode
          icon={Server}
          label="MCP Server"
          sublabel="Canadian Building Code MCP"
          badges={['10 Tools', '4 Prompts', '4 Resources']}
          color="#06b6d4"
          large
        />
        <FanOut color="#8b5cf6" />
        <motion.div variants={fadeUp} className="flex gap-3 sm:gap-6">
          <ProcessStep icon={Scissors} label="Tokenize" sublabel="Split query" color="#8b5cf6" />
          <ProcessStep icon={RefreshCw} label="Synonyms" sublabel="45 pairs" color="#a855f7" />
          <ProcessStep icon={BarChart3} label="TF-IDF" sublabel="Score & rank" color="#7c3aed" />
        </motion.div>
        <FanIn color="#8b5cf6" />
        <FlowNode
          icon={BookOpen}
          label="16 Building Code Maps"
          sublabel={
            metadata
              ? `${metadata.totalSections.toLocaleString()} sections · ${metadata.totalTables.toLocaleString()} tables`
              : 'Loading...'
          }
          badges={['13 Codes', '3 Guides', metadata ? `${metadata.totalSizeMB} MB` : '']}
          color="#8b5cf6"
        />
        <Connector color="#10b981" height={28} />
        <FlowNode
          icon={CheckCircle2}
          label="Coordinates"
          sublabel="Copyright safe — no text distributed"
          badges={['Section ID', 'Page #', 'Score', 'BBox']}
          color="#10b981"
        />
        <Connector color="#f59e0b" height={28} />
        <FlowNode
          icon={FileText}
          label="Your PDF"
          sublabel="Text extracted from your local file"
          badges={['Full Text', 'Table Data', 'Page Content']}
          color="#f59e0b"
        />
        <Connector color="#ec4899" height={28} />
        <FlowNode
          icon={Sparkles}
          label="Answer"
          sublabel="Exact section refs + extracted text"
          badges={['Section ID', 'Page Text', 'Table Data']}
          color="#ec4899"
        />
      </motion.div>

      {/* ── Desktop: Horizontal Pipeline ── */}
      <motion.div
        className="hidden md:flex flex-row items-center justify-center max-w-7xl mx-auto px-6 gap-0"
        variants={stagger}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.3 }}
      >
        <FlowNode
          icon={User}
          label="User / Claude"
          sublabel={'"Fire rating requirements?"'}
          color="#3b82f6"
          vertical
        />
        <HConnector color="#3b82f6" />
        <FlowNode
          icon={Server}
          label="MCP Server"
          sublabel="Building Code MCP"
          badges={['10 Tools', '4 Prompts', '4 Resources']}
          color="#06b6d4"
          vertical
        />
        <HConnector color="#8b5cf6" />
        <motion.div variants={fadeUp} className="flex flex-col gap-2 shrink-0">
          <ProcessStep icon={Scissors} label="Tokenize" sublabel="Split query" color="#8b5cf6" />
          <ProcessStep icon={RefreshCw} label="Synonyms" sublabel="45 pairs" color="#a855f7" />
          <ProcessStep icon={BarChart3} label="TF-IDF" sublabel="Score & rank" color="#7c3aed" />
        </motion.div>
        <HConnector color="#8b5cf6" />
        <FlowNode
          icon={BookOpen}
          label="16 Code Maps"
          sublabel={
            metadata
              ? `${metadata.totalSections.toLocaleString()} sections`
              : 'Loading...'
          }
          badges={['13 Codes', '3 Guides']}
          color="#8b5cf6"
          vertical
        />
        <HConnector color="#10b981" />
        <FlowNode
          icon={CheckCircle2}
          label="Coordinates"
          sublabel="Copyright safe"
          badges={['Section ID', 'Page #', 'BBox']}
          color="#10b981"
          vertical
        />
        <HConnector color="#f59e0b" />
        <FlowNode
          icon={FileText}
          label="Your PDF"
          sublabel="Your local file"
          badges={['Full Text', 'Tables']}
          color="#f59e0b"
          vertical
        />
        <HConnector color="#ec4899" />
        <FlowNode
          icon={Sparkles}
          label="Answer"
          sublabel="Refs + text"
          badges={['Section', 'Text']}
          color="#ec4899"
          vertical
        />
      </motion.div>
    </section>
  );
}
