"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ChatPage() {
  const [repoId, setRepoId] = useState("test_repo");
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState<{ id?: string; role: string; content: string }[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    
    // Fetch History
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    fetch(`${apiUrl}/chat/history/${repoId}`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) {
          if (res.status === 401) {
            localStorage.removeItem("token");
            router.push("/login");
          }
          throw new Error("Failed to fetch history");
        }
        return res.json();
      })
      .then(data => {
        if (data.session_id) {
          setSessionId(data.session_id);
          if (data.messages && data.messages.length > 0) {
            setChatLog(data.messages);
          } else {
            setChatLog([{ role: "ai", content: "Hello! I am BugMind AI. Ask me any questions about your codebase, or generate tests for your latest PRs!" }]);
          }
        } else {
          setSessionId(null);
          setChatLog([{ role: "ai", content: "Hello! I am BugMind AI. Ask me any questions about your codebase, or generate tests for your latest PRs!" }]);
        }
      })
      .catch(err => console.error("Failed to load history", err));
  }, [repoId, router]);

  const sendMessage = async () => {
    if (!message.trim()) return;

    const userMsg = message;
    setMessage("");
    setChatLog(prev => [...prev, { role: "user", content: userMsg }]);
    setIsTyping(true);

    const token = localStorage.getItem("token");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${apiUrl}/chat/stream`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ repo_id: repoId, message: userMsg, session_id: sessionId }),
      });

      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let aiMessage = "";
      setChatLog(prev => [...prev, { role: "ai", content: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
            // Need to fetch history to get the newly created session id if we didn't have one
            if (!sessionId) {
              const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
              fetch(`${apiUrl}/chat/history/${repoId}`, {
                headers: { "Authorization": `Bearer ${token}` }
                })
                  .then(res => res.json())
                  .then(data => {
                    if (data.session_id) setSessionId(data.session_id);
                  });
            }
            break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "").trim();
            if (dataStr === "[DONE]") break;
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);
              if (data.content) {
                aiMessage += data.content;
                setChatLog(prev => {
                  const newLog = [...prev];
                  newLog[newLog.length - 1].content = aiMessage;
                  return newLog;
                });
              } else if (data.error) {
                console.error(data.error);
              }
            } catch (err) {
              console.error("Failed to parse chunk", err);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat streaming failed", error);
    } finally {
      setIsTyping(false);
    }
  };

  const handleGenerateTests = async () => {
    setIsTyping(true);
    const token = localStorage.getItem("token");
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const res = await fetch(`${apiUrl}/chat/generate-tests`, {
        method: "POST",
        headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ repo_id: repoId, pr_number: "1" }),
      });
      const data = await res.json();
      setChatLog(prev => [...prev, { role: "ai", content: `Test generation task started! Task ID: ${data.task_id}` }]);
    } catch (e) {
      console.error("Failed to start task", e);
    } finally {
      setIsTyping(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col transition-colors duration-300">
      <nav className="w-full bg-background/80 backdrop-blur-md border-b border-border px-6 py-4 flex justify-between items-center sticky top-0 z-50 transition-colors duration-300">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-semibold tracking-tight">
            BugMind AI
          </Link>
          <div className="hidden sm:flex gap-4">
            <Link href="/dashboard" className="text-sm font-medium text-muted hover:text-foreground transition-colors">Repositories</Link>
            <Link href="/chat" className="text-sm font-medium">Copilot Chat</Link>
          </div>
        </div>
        <div className="flex gap-4 items-center">
          <button onClick={handleLogout} className="text-sm font-medium text-muted hover:text-foreground transition-colors cursor-pointer">
            Logout
          </button>
          <div className="w-8 h-8 rounded-full bg-foreground text-background flex items-center justify-center text-xs font-bold shadow-sm">
            U
          </div>
        </div>
      </nav>

      <div className="max-w-4xl w-full mx-auto p-6 flex-1 flex flex-col h-[calc(100vh-80px)]">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <h1 className="text-2xl font-bold tracking-tight">Copilot Chat</h1>
          <div className="flex gap-4 w-full sm:w-auto">
            <input 
              type="text" 
              value={repoId} 
              onChange={(e) => setRepoId(e.target.value)} 
              className="bg-card border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-muted transition-colors flex-1 sm:w-32"
              placeholder="Repo ID"
            />
            <button 
              onClick={handleGenerateTests}
              className="px-4 py-2 bg-card border border-border text-foreground rounded-md font-medium hover:bg-border/50 transition-colors text-sm shadow-sm whitespace-nowrap cursor-pointer"
            >
              Generate PR Tests
            </button>
          </div>
        </div>

        <div className="flex-1 bg-card rounded-xl border border-border overflow-hidden flex flex-col shadow-sm">
          <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6">
            {chatLog.map((log, i) => (
              <div key={i} className={`flex ${log.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-5 py-3 whitespace-pre-wrap text-sm leading-relaxed ${log.role === 'user' ? 'bg-foreground text-background' : 'bg-background border border-border text-foreground'}`}>
                  {log.content}
                </div>
              </div>
            ))}
            {isTyping && (!chatLog.length || chatLog[chatLog.length - 1].role !== 'ai') && (
              <div className="flex justify-start">
                <div className="bg-background border border-border rounded-2xl px-5 py-3 text-muted text-sm animate-pulse">
                  BugMind AI is typing...
                </div>
              </div>
            )}
          </div>
          
          <div className="p-4 border-t border-border bg-card">
            <div className="flex gap-4">
              <input 
                type="text" 
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask about your codebase..." 
                className="flex-1 bg-background border border-border rounded-lg px-4 py-3 outline-none focus:border-muted transition-colors text-foreground text-sm"
              />
              <button 
                onClick={sendMessage}
                disabled={isTyping}
                className="px-6 py-3 bg-foreground text-background rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 text-sm shadow-sm cursor-pointer"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
