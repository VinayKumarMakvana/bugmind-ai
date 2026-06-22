"use client";

import { useState, use } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, MessageSquare, Play, Shield, Terminal, X } from "lucide-react";
import Link from "next/link";

export default function PRReviewPage({ params }: { params: Promise<{ id: string; pr_id: string }> }) {
  const resolvedParams = use(params);
  const [activeLine, setActiveLine] = useState<number | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState("");
  const [messages, setMessages] = useState<{role: string, content: string}[]>([
    { role: "ai", content: "I've analyzed this PR. There is a potential SQL injection vulnerability here. Click on any line of code to ask me specific questions!" }
  ]);

  // Mock diff data
  const mockDiff = `
@@ -10,16 +10,18 @@
     
     if not client:
         print("OPENAI_API_KEY not set. Mocking AI Review.")
-        # If no API key is provided, we simulate the AI enriching the findings.
         enriched_findings = []
         for f in findings:
             f_copy = dict(f)
-            f_copy["suggested_fix"] = f"[Mock AI Context Aware] Detected '{f['description']}'..."
+            f_copy["suggested_fix"] = f"**[Mock AI Review]** Detected \`{f['description']}\`..."
             enriched_findings.append(f_copy)
         return enriched_findings
 
-    # Build the prompt
-    system_prompt = "You are BugMind AI, an expert Senior Software Engineer."
+    system_prompt = (
+        "You are BugMind AI, an elite Senior Staff Software Engineer."
+    )
  `.trim().split('\n');

  const handleLineClick = (lineNum: number) => {
    setActiveLine(lineNum);
    setChatOpen(true);
  };

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;
    
    setMessages([...messages, { role: "user", content: chatMessage }]);
    setChatMessage("");
    
    // Mock AI response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: "ai", 
        content: `Analyzing line ${activeLine}... This looks correct according to the latest standards. The RAG context shows no conflicting imports.` 
      }]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col relative overflow-hidden">
      {/* Top Nav */}
      <nav className="w-full glass px-6 py-4 flex items-center justify-between sticky top-0 z-50 border-b border-border/50">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="h-6 w-px bg-border"></div>
          <div>
            <h1 className="text-lg font-bold">Fix Auth Middleware</h1>
            <div className="text-xs text-muted flex items-center gap-2">
              <span className="text-primary font-medium">PR #{resolvedParams.pr_id}</span>
              <span>•</span>
              <span>backend-service</span>
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-card border border-border rounded-md text-sm font-semibold hover:border-primary/50 transition-colors flex items-center gap-2">
            <Terminal className="w-4 h-4" /> Run Tests
          </button>
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-semibold hover:bg-primary/90 transition-colors flex items-center gap-2 shadow-[0_0_15px_rgba(124,58,237,0.3)]">
            <Play className="w-4 h-4" /> Auto-Fix Issues
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden">
        {/* Diff Viewer */}
        <div className={`flex-1 overflow-y-auto p-6 transition-all duration-300 ${chatOpen ? 'mr-96' : ''}`}>
          <div className="max-w-5xl mx-auto">
            <div className="mb-6 flex items-center justify-between">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Shield className="w-5 h-5 text-accent" />
                Security Analysis
              </h2>
              <div className="px-3 py-1 bg-red-500/10 text-red-400 border border-red-500/20 rounded-full text-xs font-bold">
                1 High Severity Finding
              </div>
            </div>

            {/* Code Diff Component */}
            <div className="rounded-xl overflow-hidden border border-border shadow-2xl font-mono text-sm">
              <div className="bg-card px-4 py-2 border-b border-border text-muted flex justify-between">
                <span>src/services/ai_reviewer.py</span>
                <span>Python</span>
              </div>
              <div className="bg-[#0a0a0c] overflow-x-auto">
                {mockDiff.map((line, idx) => {
                  const isAdd = line.startsWith('+');
                  const isRemove = line.startsWith('-');
                  const isContext = line.startsWith('@@');
                  const isActive = activeLine === idx;

                  let rowClass = "hover:bg-white/5 cursor-pointer flex group ";
                  if (isAdd) rowClass += "bg-green-500/10 text-green-300 ";
                  else if (isRemove) rowClass += "bg-red-500/10 text-red-300 ";
                  else if (isContext) rowClass += "bg-blue-500/5 text-blue-400 ";
                  else rowClass += "text-gray-300 ";

                  if (isActive) rowClass += "border-l-2 border-primary bg-primary/10 ";

                  return (
                    <div 
                      key={idx} 
                      className={rowClass}
                      onClick={() => handleLineClick(idx)}
                    >
                      <div className="w-12 text-right pr-4 text-xs text-muted select-none py-1 border-r border-border/30 group-hover:text-foreground">
                        {isContext ? ' ' : idx + 10}
                      </div>
                      <div className="pl-4 py-1 whitespace-pre">
                        {line}
                      </div>
                      <div className="ml-auto pr-4 opacity-0 group-hover:opacity-100 flex items-center">
                        <MessageSquare className="w-3 h-3 text-muted" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Floating Chat Panel */}
        <AnimatePresence>
          {chatOpen && (
            <motion.div 
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="w-96 glass border-l border-border/50 fixed right-0 top-[73px] bottom-0 flex flex-col z-40 shadow-[-10px_0_30px_rgba(0,0,0,0.5)]"
            >
              <div className="p-4 border-b border-border flex justify-between items-center bg-card/50">
                <h3 className="font-bold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
                  AI Copilot
                </h3>
                <button onClick={() => setChatOpen(false)} className="w-8 h-8 rounded-full hover:bg-white/10 flex items-center justify-center transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {activeLine !== null && (
                  <div className="text-xs text-muted bg-black/30 p-2 rounded border border-border/50 font-mono mb-4">
                    Context: Line {activeLine + 10}
                  </div>
                )}
                {messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-br-sm' : 'bg-card border border-border rounded-bl-sm'}`}>
                      {msg.content}
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 border-t border-border bg-card/50">
                <form onSubmit={handleChatSubmit} className="relative">
                  <input 
                    type="text" 
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    placeholder="Ask about this code..."
                    className="w-full bg-background border border-border rounded-full pl-4 pr-10 py-2.5 text-sm focus:outline-none focus:border-primary/50 transition-colors"
                  />
                  <button type="submit" className="absolute right-2 top-1.5 w-7 h-7 rounded-full bg-primary flex items-center justify-center text-primary-foreground hover:bg-primary/90 transition-colors">
                    <ArrowLeft className="w-3 h-3 rotate-180" />
                  </button>
                </form>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
