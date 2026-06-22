"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Shield, GitPullRequest, AlertCircle, Activity, LogOut, ChevronRight, Settings } from "lucide-react";

type RepoData = {
  id: string;
  name: string;
  prs: number;
  issues: number;
  score: number;
};

export default function Dashboard() {
  const [repos, setRepos] = useState<RepoData[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const fetchDashboard = () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://bugmind-ai.onrender.com/api/v1";
      fetch(`${apiUrl}/repos/dashboard`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
        .then(res => {
          if (!res.ok) {
            if (res.status === 401) {
              localStorage.removeItem("token");
              router.push("/login");
            }
            throw new Error("Failed to fetch dashboard data");
          }
          return res.json();
        })
        .then(data => {
          setRepos(data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Failed to fetch dashboard data:", err);
          setLoading(false);
        });
    };

    fetchDashboard();

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://bugmind-ai.onrender.com/api/v1";
    const eventSource = new EventSource(`${apiUrl}/stream/events`);
    eventSource.addEventListener("update", (event) => {
      fetchDashboard();
    });

    return () => {
      eventSource.close();
    };
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const handleConnectGithub = () => {
    const token = localStorage.getItem("token");
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://bugmind-ai.onrender.com/api/v1";
    if (token) {
      window.location.href = `${apiUrl}/github/login?token=${token}`;
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.05 } }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <nav className="w-full border-b border-border/50 bg-background/80 backdrop-blur-md px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="w-8 h-8 rounded-md bg-foreground flex items-center justify-center">
              <Shield className="w-4 h-4 text-background" />
            </div>
            <span className="text-xl font-bold tracking-tight">BugMind</span>
          </Link>
          <div className="h-4 w-px bg-border hidden sm:block mx-2"></div>
          <div className="hidden sm:flex gap-6">
            <Link href="/dashboard" className="text-sm font-medium text-foreground">Repositories</Link>
          </div>
        </div>
        <div className="flex gap-4 items-center">
          <Link href="/settings" className="text-sm font-medium text-muted hover:text-foreground transition-colors flex items-center gap-2">
            <Settings className="w-4 h-4" /> Settings
          </Link>
          <button onClick={handleLogout} className="text-sm font-medium text-muted hover:text-red-500 transition-colors cursor-pointer flex items-center gap-2">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </nav>

      <main className="flex-1 max-w-6xl mx-auto w-full p-6 mt-8">
        <motion.div initial="hidden" animate="visible" variants={containerVariants} className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-10 gap-4">
          <motion.div variants={itemVariants}>
            <h1 className="text-3xl font-bold mb-2 tracking-tight">Repositories</h1>
            <p className="text-muted text-sm">Manage connected GitHub repos and monitor AI health scores.</p>
          </motion.div>
          <motion.button onClick={handleConnectGithub} variants={itemVariants} className="px-5 py-2 bg-foreground text-background font-semibold rounded-md hover:bg-foreground/90 transition-colors flex items-center gap-2 text-sm">
            <GitPullRequest className="w-4 h-4" /> Add Repository
          </motion.button>
        </motion.div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 space-y-4">
            <div className="w-5 h-5 rounded-full border-2 border-muted border-t-foreground animate-spin"></div>
            <p className="text-muted text-sm">Loading...</p>
          </div>
        ) : repos.length === 0 ? (
          <div className="col-span-full py-20 flex flex-col items-center justify-center text-center border border-dashed border-border rounded-xl bg-card/30">
            <GitPullRequest className="w-8 h-8 text-muted mb-4" />
            <h3 className="text-base font-semibold text-foreground">No repositories found</h3>
            <p className="mt-1 text-sm text-muted">Connect your GitHub account to start reviewing code.</p>
            <button onClick={handleConnectGithub} className="mt-6 px-5 py-2 bg-card border border-border text-sm font-medium rounded-md hover:bg-card/80 transition-colors">
              Connect Account
            </button>
          </div>
        ) : (
          <motion.div variants={containerVariants} initial="hidden" animate="visible" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {repos.map((repo) => (
              <motion.div key={repo.id} variants={itemVariants} className="p-5 rounded-xl border border-border bg-card hover:border-muted transition-all cursor-pointer group flex flex-col min-h-[180px]">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="font-semibold text-lg text-foreground group-hover:text-accent transition-colors">
                    {repo.name}
                  </h3>
                  <div className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                    repo.score > 90 ? 'bg-green-500/10 text-green-500 border-green-500/20' : 
                    repo.score > 80 ? 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20' : 
                    'bg-red-500/10 text-red-500 border-red-500/20'
                  }`}>
                    Score {repo.score}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-3 mt-auto">
                  <div className="bg-background rounded-lg border border-border p-3">
                    <div className="text-xs text-muted font-medium mb-1 flex items-center gap-1">
                      <GitPullRequest className="w-3 h-3" /> PRs
                    </div>
                    <span className="font-semibold">{repo.prs}</span>
                  </div>
                  <div className="bg-background rounded-lg border border-border p-3">
                    <div className="text-xs text-muted font-medium mb-1 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> Issues
                    </div>
                    <span className="font-semibold">{repo.issues}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </main>
    </div>
  );
}
