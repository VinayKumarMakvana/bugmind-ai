"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import Editor from "@monaco-editor/react";
import { Play, Loader2, Sparkles, AlertCircle, ChevronDown, Check, TerminalSquare, X, Layout } from "lucide-react";
import ReactMarkdown from "react-markdown";

const LANGUAGES = [
  { id: "javascript", name: "JavaScript", ext: "js" },
  { id: "typescript", name: "TypeScript", ext: "ts" },
  { id: "python", name: "Python", ext: "py" },
  { id: "java", name: "Java", ext: "java" },
  { id: "cpp", name: "C++", ext: "cpp" },
  { id: "csharp", name: "C#", ext: "cs" },
  { id: "go", name: "Go", ext: "go" },
  { id: "rust", name: "Rust", ext: "rs" },
  { id: "php", name: "PHP", ext: "php" },
  { id: "ruby", name: "Ruby", ext: "rb" },
  { id: "swift", name: "Swift", ext: "swift" },
  { id: "kotlin", name: "Kotlin", ext: "kt" },
  { id: "dart", name: "Dart", ext: "dart" },
  { id: "sql", name: "SQL", ext: "sql" },
  { id: "json", name: "JSON", ext: "json" },
  { id: "yaml", name: "YAML", ext: "yaml" },
  { id: "markdown", name: "Markdown", ext: "md" },
  { id: "shell", name: "Shell/Bash", ext: "sh" },
  { id: "html", name: "HTML", ext: "html" },
  { id: "css", name: "CSS", ext: "css" },
];

export default function EditorPage() {
  const router = useRouter();
  const [code, setCode] = useState<string>("// Paste your code here to analyze...");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<{ summary?: string, bugs?: { severity: string, title: string, description: string }[] } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [executionOutput, setExecutionOutput] = useState<{ status: string, output: string } | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [showTerminal, setShowTerminal] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [editorFontSize, setEditorFontSize] = useState(14);
  const [selectedLang, setSelectedLang] = useState(LANGUAGES[0]);
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false);
  const langMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (langMenuRef.current && !langMenuRef.current.contains(event.target as Node)) {
        setIsLangMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    }

    const handleResize = () => {
      setEditorFontSize(window.innerWidth < 480 ? 10 : window.innerWidth < 768 ? 12 : 14);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [router]);

  const handleAnalyze = async () => {
    if (!code.trim()) return;
    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const token = localStorage.getItem("token");
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
      
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          code_content: code,
          file_name: `snippet.${selectedLang.ext}`
        })
      });

      if (!response.ok) {
        throw new Error("Analysis failed. Check backend connection.");
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRunCode = async () => {
    if (!code.trim()) return;
    setShowTerminal(true);
    setExecutionOutput(null);

    // Handle HTML & CSS Live Preview
    if (selectedLang.id === "html") {
      setExecutionOutput({ status: "preview", output: code });
      return;
    }
    
    if (selectedLang.id === "css") {
      const wrappedCss = `
        <!DOCTYPE html>
        <html>
        <head>
          <style>${code}</style>
        </head>
        <body>
          <div class="preview-container" style="padding: 20px; font-family: sans-serif;">
            <h1>CSS Preview</h1>
            <p>This is a sample paragraph to test your CSS styles.</p>
            <button>Sample Button</button>
            <div class="box">A Box</div>
          </div>
        </body>
        </html>
      `;
      setExecutionOutput({ status: "preview", output: wrappedCss });
      return;
    }

    setIsExecuting(true);

    try {
      const token = localStorage.getItem("token");
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";
      
      const response = await fetch(`${API_URL}/execute`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          code_content: code,
          language: selectedLang.id
        })
      });

      if (!response.ok) {
        throw new Error("Execution failed. Check backend connection.");
      }

      const data = await response.json();
      setExecutionOutput(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setExecutionOutput({ status: "error", output: err.message });
      } else {
        setExecutionOutput({ status: "error", output: "Something went wrong during execution." });
      }
    } finally {
      setIsExecuting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Frosted Glass Navbar */}
      <nav className="w-full bg-background/80 backdrop-blur-md border-b border-border px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.png" alt="Logo" width={28} height={28} className="rounded-md" />
            <span className="text-xl font-bold tracking-tight">BugMind<span className="text-primary">.ai</span></span>
          </Link>
          <span className="px-2 py-1 rounded-full bg-card border border-border text-xs font-medium text-muted ml-4">
            Web IDE
          </span>
        </div>
        
        <div className="flex gap-4 items-center">
          <button 
            onClick={handleRunCode}
            disabled={isExecuting}
            className="flex items-center gap-2 px-5 py-2 bg-green-500/10 text-green-500 border border-green-500/20 rounded-full text-sm font-medium hover:bg-green-500/20 transition-colors disabled:opacity-50 gemini-shadow cursor-pointer"
          >
            {isExecuting ? <Loader2 className="w-4 h-4 animate-spin" /> : <TerminalSquare className="w-4 h-4" />}
            Run Code
          </button>
          <button 
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-5 py-2 bg-primary text-primary-foreground rounded-full text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50 gemini-shadow cursor-pointer"
          >
            {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Run Analysis
          </button>
          <button onClick={handleLogout} className="text-sm font-medium text-muted hover:text-foreground transition-colors cursor-pointer ml-4">
            Logout
          </button>
        </div>
      </nav>

      {/* Floating Card Layout */}
      <div className="flex-1 flex flex-col md:flex-row gap-6 p-6 h-auto md:h-[calc(100vh-73px)] max-w-[1800px] w-full mx-auto">
        
        {/* Editor & Terminal Column */}
        <div className="flex-1 flex flex-col gap-6 min-h-[400px] md:min-h-0">
          
          {/* Editor Card */}
          <div className="flex-1 rounded-3xl border border-border bg-card gemini-shadow overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-border flex justify-between items-center bg-card">
            <h2 className="text-sm font-semibold tracking-wide text-muted uppercase">Code Editor</h2>
            <div className="relative" ref={langMenuRef}>
              <button
                onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
                className="flex items-center gap-2 bg-background border border-border hover:border-primary text-foreground text-xs font-medium rounded-md px-3 py-1.5 transition-colors cursor-pointer"
              >
                {selectedLang.name}
                <ChevronDown className={`w-3 h-3 transition-transform ${isLangMenuOpen ? "rotate-180" : ""}`} />
              </button>
              
              {isLangMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 max-h-64 overflow-y-auto bg-card border border-border rounded-lg shadow-xl z-50 py-1 flex flex-col gemini-shadow animate-in fade-in slide-in-from-top-2">
                  {LANGUAGES.map(lang => (
                    <button
                      key={lang.id}
                      onClick={() => {
                        setSelectedLang(lang);
                        setIsLangMenuOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2.5 text-sm flex items-center justify-between hover:bg-background transition-colors cursor-pointer ${selectedLang.id === lang.id ? "text-primary bg-primary/5 font-medium" : "text-foreground"}`}
                    >
                      {lang.name}
                      {selectedLang.id === lang.id && <Check className="w-4 h-4 text-primary" />}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div className="flex-1 w-full bg-[#1e1e1e]">
            <Editor
              height="100%"
              language={selectedLang.id}
              theme="vs-dark"
              defaultValue={code}
              onChange={(value) => setCode(value || "")}
              options={{
                minimap: { enabled: false },
                fontSize: editorFontSize,
                padding: { top: 20 },
                scrollBeyondLastLine: false,
                roundedSelection: false,
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace"
              }}
            />
          </div>
        </div>

        {/* Terminal/Preview Card */}
        {showTerminal && (
          <div className="h-[250px] shrink-0 rounded-3xl border border-border bg-card gemini-shadow overflow-hidden flex flex-col animate-in slide-in-from-bottom-4 duration-500">
            <div className="px-6 py-3 border-b border-border flex justify-between items-center bg-card">
              <div className="flex items-center gap-2">
                {executionOutput?.status === "preview" ? (
                  <Layout className="w-4 h-4 text-muted" />
                ) : (
                  <TerminalSquare className="w-4 h-4 text-muted" />
                )}
                <h2 className="text-sm font-semibold tracking-wide text-muted uppercase">
                  {executionOutput?.status === "preview" ? "Live Preview" : "Terminal Output"}
                </h2>
              </div>
              <button onClick={() => setShowTerminal(false)} className="text-muted hover:text-foreground transition-colors cursor-pointer">
                <X className="w-4 h-4" />
              </button>
            </div>
            
            {executionOutput?.status === "preview" ? (
              <div className="flex-1 bg-white overflow-hidden">
                <iframe
                  srcDoc={executionOutput.output}
                  className="w-full h-full border-0"
                  title="Live Preview"
                  sandbox="allow-scripts"
                />
              </div>
            ) : (
              <div className="flex-1 p-4 bg-[#1e1e1e] overflow-y-auto font-mono text-sm">
                {isExecuting ? (
                  <div className="flex items-center gap-3 text-muted animate-pulse">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Executing code...</span>
                  </div>
                ) : executionOutput ? (
                  <pre className={`whitespace-pre-wrap ${executionOutput.status === 'error' ? 'text-red-400' : 'text-green-400'}`}>
                    {executionOutput.output}
                  </pre>
                ) : (
                  <span className="text-muted">No output</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* AI Assistant Card */}
        <div className="w-full md:w-[450px] lg:w-[500px] min-h-[400px] md:min-h-0 rounded-3xl border border-border bg-card gemini-shadow overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-border flex items-center gap-2 bg-card">
            <Sparkles className="w-4 h-4 text-accent" />
            <h2 className="text-sm font-semibold tracking-wide text-accent uppercase">AI Analysis</h2>
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto bg-glass">
            {!isAnalyzing && !analysisResult && !error && (
              <div className="h-full flex flex-col items-center justify-center text-center opacity-70">
                <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mb-6">
                  <Sparkles className="w-8 h-8 text-accent animate-pulse" />
                </div>
                <h3 className="text-xl font-medium mb-2 gemini-gradient-text">Ready to assist</h3>
                <p className="text-sm text-muted max-w-xs leading-relaxed">
                  Paste your code and click Run Analysis to instantly detect bugs, vulnerabilities, and get optimized solutions.
                </p>
              </div>
            )}

            {isAnalyzing && (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <Loader2 className="w-10 h-10 text-accent animate-spin mb-4" />
                <p className="text-sm font-medium text-foreground animate-pulse">Analyzing codebase...</p>
              </div>
            )}

            {error && (
              <div className="p-4 rounded-2xl border border-red-500/20 bg-red-500/10 text-red-500 flex gap-3 text-sm">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <p>{error}</p>
              </div>
            )}

            {analysisResult && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="p-5 rounded-2xl bg-accent/5 border border-accent/10">
                  <h3 className="font-semibold text-lg mb-2 text-foreground flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-accent" />
                    Review Summary
                  </h3>
                  <p className="text-sm text-muted leading-relaxed whitespace-pre-wrap">
                    {analysisResult.summary || "Analysis completed successfully."}
                  </p>
                </div>
                
                {analysisResult.bugs && analysisResult.bugs.length > 0 && (
                  <div className="space-y-4">
                    <h4 className="text-sm font-semibold tracking-wide text-muted uppercase pl-2">Detected Issues</h4>
                    {analysisResult.bugs.map((bug, i: number) => (
                      <div key={i} className="p-4 rounded-2xl border border-border bg-card">
                        <div className="flex gap-2 mb-2">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            bug.severity === 'critical' ? 'bg-red-500/10 text-red-500' : 
                            bug.severity === 'high' ? 'bg-orange-500/10 text-orange-500' : 
                            'bg-yellow-500/10 text-yellow-500'
                          }`}>
                            {bug.severity}
                          </span>
                        </div>
                        <h5 className="font-medium text-sm mb-1">{bug.title}</h5>
                        <div className="text-xs text-muted leading-relaxed prose prose-invert max-w-none prose-sm prose-pre:bg-black/50 prose-pre:border prose-pre:border-border">
                          <ReactMarkdown>{bug.description}</ReactMarkdown>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
