import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '3D Visualizer - Canadian Building Code MCP',
  description: 'Interactive 3D visualization of how the MCP server processes building code queries',
  openGraph: {
    title: '3D Visualizer - Canadian Building Code MCP',
    description: 'Explore how the MCP server searches and retrieves Canadian Building Code sections',
  },
};

export default function VisualizerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
