'use client';

import { useState } from 'react';
import { Building, Landmark, BookOpen, ChevronDown } from 'lucide-react';

const codeGroups = [
  {
    title: 'National Codes',
    icon: Landmark,
    color: 'bg-blue-500',
    codes: [
      { name: 'NBC 2025', full: 'National Building Code', sections: '4,200+' },
      { name: 'NFC 2025', full: 'National Fire Code', sections: '1,400+' },
      { name: 'NPC 2025', full: 'National Plumbing Code', sections: '590+' },
      { name: 'NECB 2025', full: 'National Energy Code', sections: '770+' },
    ],
  },
  {
    title: 'Provincial Codes',
    icon: Building,
    color: 'bg-emerald-500',
    codes: [
      { name: 'OBC', full: 'Ontario Building Code', sections: '3,900+', province: 'ON' },
      { name: 'BCBC 2024', full: 'BC Building Code', sections: '2,600+', province: 'BC' },
      { name: 'ABC', full: 'Alberta Building Code', sections: '4,100+', province: 'AB' },
      { name: 'QCC', full: 'Quebec Construction Code', sections: '3,900+', province: 'QC' },
    ],
  },
  {
    title: "User's Guides",
    icon: BookOpen,
    color: 'bg-amber-500',
    codes: [
      { name: 'Part 9 Guide', full: 'Housing & Small Buildings', sections: '1,300+' },
      { name: 'Part 4 Guide', full: 'Structural Design', sections: '20+' },
      { name: 'NECB Guide', full: 'Energy Code Guide', sections: '610+' },
    ],
  },
];

export default function CodeList() {
  const [openAccordion, setOpenAccordion] = useState<number | null>(0);

  const toggleAccordion = (index: number) => {
    setOpenAccordion(openAccordion === index ? null : index);
  };

  return (
    <section id="codes" className="py-24 bg-white border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium mb-4">
            Supported Codes
          </span>
          <h2 className="text-3xl md:text-4xl font-bold mb-4 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            Comprehensive Coverage
          </h2>
          <p className="text-slate-600 max-w-xl mx-auto">
            From National Codes to Provincial Codes and User Guides,
            we support all major Canadian building codes.
          </p>
        </div>

        {/* Desktop Grid */}
        <div className="hidden md:grid md:grid-cols-3 gap-8">
          {codeGroups.map((group) => (
            <div key={group.title}>
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden h-full hover:shadow-lg hover:border-cyan-200 hover:-translate-y-1 transition-all duration-300">
                {/* Header */}
                <div className={`${group.color} p-4 flex items-center gap-3`}>
                  <group.icon className="w-6 h-6 text-white" />
                  <h3 className="text-lg font-bold text-white">{group.title}</h3>
                </div>

                {/* Code list */}
                <div className="p-4 space-y-3">
                  {group.codes.map((code) => (
                    <div
                      key={code.name}
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
                        {code.sections} sections
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Mobile Accordion */}
        <div className="md:hidden space-y-3">
          {codeGroups.map((group, groupIndex) => (
            <div key={group.title} className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
              {/* Accordion Header */}
              <button
                onClick={() => toggleAccordion(groupIndex)}
                className={`${group.color} p-4 flex items-center justify-between w-full`}
              >
                <div className="flex items-center gap-3">
                  <group.icon className="w-5 h-5 text-white" />
                  <h3 className="text-base font-bold text-white">{group.title}</h3>
                </div>
                <ChevronDown
                  className={`w-5 h-5 text-white transition-transform duration-300 ${
                    openAccordion === groupIndex ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {/* Accordion Content */}
              {openAccordion === groupIndex && (
                <div className="p-3 space-y-2">
                  {group.codes.map((code) => (
                    <div
                      key={code.name}
                      className="p-3 bg-slate-50 rounded-lg"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-slate-900 text-sm">
                          {code.name}
                        </span>
                        {'province' in code && (
                          <span className="text-xs bg-slate-200 text-slate-600 px-2 py-0.5 rounded">
                            {code.province}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-slate-500">
                        {code.full} • {code.sections} sections
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
