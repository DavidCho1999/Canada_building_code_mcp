'use client';

import { motion } from 'framer-motion';
import { Building, Landmark, BookOpen } from 'lucide-react';

const codeGroups = [
  {
    title: 'National Codes',
    icon: Landmark,
    color: 'bg-blue-500',
    codes: [
      { name: 'NBC 2025', full: 'National Building Code', sections: 4213 },
      { name: 'NFC 2025', full: 'National Fire Code', sections: 1407 },
      { name: 'NPC 2025', full: 'National Plumbing Code', sections: 595 },
      { name: 'NECB 2025', full: 'National Energy Code', sections: 777 },
    ],
  },
  {
    title: 'Provincial Codes',
    icon: Building,
    color: 'bg-emerald-500',
    codes: [
      { name: 'OBC', full: 'Ontario Building Code', sections: 3925, province: 'ON' },
      { name: 'BCBC 2024', full: 'BC Building Code', sections: 2645, province: 'BC' },
      { name: 'ABC', full: 'Alberta Building Code', sections: 4165, province: 'AB' },
      { name: 'QCC', full: 'Quebec Construction Code', sections: 3925, province: 'QC' },
    ],
  },
  {
    title: "User's Guides",
    icon: BookOpen,
    color: 'bg-amber-500',
    codes: [
      { name: 'Part 9 Guide', full: 'Housing & Small Buildings', sections: 1399 },
      { name: 'Part 4 Guide', full: 'Structural Design', sections: 21 },
      { name: 'NECB Guide', full: 'Energy Code Guide', sections: 612 },
    ],
  },
];

export default function CodeList() {
  return (
    <section id="codes" className="py-24 bg-white border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <span className="inline-block px-4 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium mb-4">
            Supported Codes
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent">
            Comprehensive Coverage
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto">
            From National Codes to Provincial Codes and User Guides,
            we support all major Canadian building codes.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {codeGroups.map((group, groupIndex) => (
            <motion.div
              key={group.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: groupIndex * 0.1 }}
            >
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden h-full hover:shadow-lg hover:border-cyan-200 hover:-translate-y-1 transition-all duration-300">
                {/* Header */}
                <div className={`${group.color} p-4 flex items-center gap-3`}>
                  <group.icon className="w-6 h-6 text-white" />
                  <h3 className="text-lg font-bold text-white">{group.title}</h3>
                </div>

                {/* Code list */}
                <div className="p-4 space-y-3">
                  {group.codes.map((code, index) => (
                    <motion.div
                      key={code.name}
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.3, delay: groupIndex * 0.1 + index * 0.05 }}
                      className="group p-3 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors cursor-default"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-slate-900">
                          {code.name}
                        </span>
                        {'province' in code && (
                          <span className="text-xs bg-slate-200 text-slate-600 px-2 py-0.5 rounded">
                            {code.province}
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-slate-500 mb-1">
                        {code.full}
                      </div>
                      <div className="text-xs text-slate-400">
                        {code.sections.toLocaleString()} sections
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
}
