export default function Footer() {
  return (
    <footer className="py-8 border-t border-slate-200">
      <div className="max-w-6xl mx-auto px-6 text-center">
        <p className="text-sm text-slate-400">
          © {new Date().getFullYear()} BuildingCode MCP
        </p>
      </div>
    </footer>
  );
}
