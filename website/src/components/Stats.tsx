'use client';

import { useEffect, useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { FileText, Building2, MapPin } from 'lucide-react';

const stats = [
  {
    icon: FileText,
    value: 25707,
    label: 'Sections',
  },
  {
    icon: Building2,
    value: 14,
    label: 'Codes',
  },
  {
    icon: MapPin,
    value: 5,
    label: 'Provinces',
  },
];

function AnimatedNumber({ value }: { value: number }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;

    const duration = 2000;
    const steps = 60;
    const stepValue = value / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += stepValue;
      if (current >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [isInView, value]);

  return (
    <span ref={ref}>
      {count.toLocaleString()}
    </span>
  );
}

export default function Stats() {
  return (
    <section className="py-16 bg-white">
      <div className="max-w-4xl mx-auto px-6">
        <div className="grid grid-cols-3 gap-6">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="text-center"
            >
              <div className="inline-flex items-center justify-center w-10 h-10 bg-slate-100 text-slate-600 rounded-xl mb-3">
                <stat.icon className="w-5 h-5" />
              </div>
              <div className="text-3xl md:text-4xl font-bold text-slate-900 mb-1">
                <AnimatedNumber value={stat.value} />
              </div>
              <div className="text-sm text-slate-500">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
