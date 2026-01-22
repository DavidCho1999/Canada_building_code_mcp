'use client';

import { motion } from 'framer-motion';
import { Github, ArrowRight, Copy, Check } from 'lucide-react';
import { useState } from 'react';

export default function CTA() {
  const [copied, setCopied] = useState(false);

  const configCode = `{
  "mcpServers": {
    "building-code": {
      "command": "uvx",
      "args": ["building-code-mcp"]
    }
  }
}`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(configCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="setup" className="py-20 bg-white border-t border-slate-200">
      <div className="max-w-4xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <span className="inline-block px-4 py-1 bg-cyan-100 text-cyan-700 rounded-full text-sm font-medium mb-4">
            Get Started
          </span>
          <h2 className="text-2xl md:text-3xl font-bold mb-8 pb-1 bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent hover:from-blue-600 hover:to-cyan-500 hover:drop-shadow-[0_0_15px_rgba(6,182,212,0.5)] transition-all duration-300 cursor-default">
            Quick Setup
          </h2>

          {/* Setup Steps */}
          <div className="space-y-6 mb-10 text-left">
            {/* Step 1 */}
            <div className="flex gap-4">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                1
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 mb-2">Install the package</h3>
                <div className="bg-slate-900 rounded-lg p-3 font-mono text-sm text-slate-300">
                  pip install building-code-mcp
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                2
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 mb-2">Add to Claude Desktop config</h3>
                <div className="text-xs text-slate-500 mb-2 space-y-1">
                  <p className="break-all"><span className="font-medium">Windows:</span> %APPDATA%\Claude\claude_desktop_config.json</p>
                  <p className="break-all"><span className="font-medium">Mac:</span> ~/Library/Application Support/Claude/claude_desktop_config.json</p>
                </div>
                <div className="relative">
                  <pre className="bg-slate-900 rounded-lg p-3 font-mono text-sm text-slate-300 overflow-x-auto">
                    {configCode}
                  </pre>
                  <button
                    onClick={copyToClipboard}
                    className="absolute top-2 right-2 p-2 bg-slate-700 hover:bg-slate-600 rounded text-slate-300 transition-colors"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                3
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 mb-2">Restart Claude Desktop and start asking</h3>
                <p className="text-slate-600 text-sm">
                  That&apos;s it! Ask questions like &quot;What is the minimum stair width in OBC?&quot;
                </p>
              </div>
            </div>
          </div>

          {/* GitHub Button */}
          <div className="text-center">
            <a
              href="https://github.com/DavidCho1999/Canada-AEC-Code-MCP"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-3 bg-gradient-to-r from-slate-800 to-slate-900 text-white px-8 py-4 rounded-xl font-medium hover:scale-105 hover:shadow-xl hover:shadow-slate-900/30 transition-all duration-300"
            >
              <Github className="w-5 h-5" />
              View on GitHub
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
