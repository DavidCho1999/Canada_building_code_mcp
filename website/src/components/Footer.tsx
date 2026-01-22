import CodeStatus from './CodeStatus';

export default function Footer() {
  return (
    <footer className="py-8 border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-6 flex flex-col items-center gap-4">
        <CodeStatus />
        <p className="text-sm text-slate-400">
          © {new Date().getFullYear()} BuildingCode MCP. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
