import { Github } from 'lucide-react';
import CodeStatus from './CodeStatus';

export default function Footer() {
  return (
    <footer className="py-12 border-t border-slate-200 bg-slate-50">
      <div className="max-w-6xl mx-auto px-6 flex flex-col items-center gap-6">
        <a
          href="https://github.com/DavidCho1999/Canada-AEC-Code-MCP"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 bg-slate-900 text-white px-6 py-3 rounded-xl font-medium hover:bg-slate-800 hover:scale-105 transition-all duration-300"
        >
          <Github className="w-5 h-5" />
          View on GitHub
        </a>

        <CodeStatus />

        <p className="text-sm text-slate-400">
          © {new Date().getFullYear()} BuildingCode MCP. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
