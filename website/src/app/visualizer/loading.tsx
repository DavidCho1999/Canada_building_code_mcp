export default function Loading() {
  return (
    <div className="flex items-center justify-center h-screen bg-slate-900">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-white text-lg">Loading Visualizer...</p>
        <p className="text-slate-400 text-sm mt-2">
          Preparing 3D environment
        </p>
      </div>
    </div>
  );
}
