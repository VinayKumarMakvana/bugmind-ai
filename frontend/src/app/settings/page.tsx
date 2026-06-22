"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Shield, Settings, Save, ArrowLeft, Key } from "lucide-react";

export default function SettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });
  
  const [profile, setProfile] = useState({
    name: "",
    email: "",
    openai_api_key: "",
    github_access_token: ""
  });

  const [hasOpenAIKey, setHasOpenAIKey] = useState(false);
  const [hasGitHubToken, setHasGitHubToken] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const fetchProfile = async () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://bugmind-ai.onrender.com/api/v1";
      try {
        const res = await fetch(`${apiUrl}/auth/me`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (!res.ok) {
          if (res.status === 401) {
            localStorage.removeItem("token");
            router.push("/login");
          }
          throw new Error("Failed to load profile");
        }
        
        const data = await res.json();
        setProfile(prev => ({
          ...prev,
          name: data.name,
          email: data.email
        }));
        setHasOpenAIKey(data.has_openai_key);
        setHasGitHubToken(data.has_github_token);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };

    fetchProfile();
  }, [router]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ text: "", type: "" });

    const token = localStorage.getItem("token");
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://bugmind-ai.onrender.com/api/v1";
    
    // Only send the fields that have been typed into (to not overwrite existing hidden keys with empty string)
    const updatePayload: any = { name: profile.name };
    if (profile.openai_api_key) updatePayload.openai_api_key = profile.openai_api_key;
    if (profile.github_access_token) updatePayload.github_access_token = profile.github_access_token;

    try {
      const res = await fetch(`${apiUrl}/auth/me`, {
        method: "PUT",
        headers: { 
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(updatePayload)
      });
      
      if (!res.ok) throw new Error("Failed to update settings");
      
      const data = await res.json();
      setHasOpenAIKey(data.has_openai_key);
      setHasGitHubToken(data.has_github_token);
      
      // Clear input fields after saving (keys are hidden)
      setProfile(prev => ({ ...prev, openai_api_key: "", github_access_token: "" }));
      setMessage({ text: "Settings saved successfully", type: "success" });
    } catch (err) {
      setMessage({ text: "Error saving settings", type: "error" });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage({ text: "", type: "" }), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <nav className="w-full border-b border-border/50 bg-background/80 backdrop-blur-md px-6 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="flex items-center gap-2 text-muted hover:text-foreground transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
          </Link>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-md bg-foreground flex items-center justify-center">
            <Shield className="w-4 h-4 text-background" />
          </div>
          <span className="text-xl font-bold tracking-tight hidden sm:block">BugMind</span>
        </div>
      </nav>

      <main className="flex-1 max-w-3xl mx-auto w-full p-6 mt-8">
        <div className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight mb-2 flex items-center gap-3">
            <Settings className="w-8 h-8" /> Profile Settings
          </h1>
          <p className="text-muted text-sm">Manage your personal details and third-party API integrations.</p>
        </div>

        {loading ? (
          <div className="py-20 flex justify-center">
            <div className="w-5 h-5 rounded-full border-2 border-muted border-t-foreground animate-spin"></div>
          </div>
        ) : (
          <form onSubmit={handleSave} className="space-y-8">
            <div className="p-6 border border-border bg-card rounded-xl">
              <h2 className="text-lg font-semibold mb-4">Personal Information</h2>
              <div className="grid gap-4">
                <div>
                  <label className="block text-sm font-medium text-muted mb-1">Email Address</label>
                  <input 
                    type="email" 
                    value={profile.email}
                    disabled
                    className="w-full bg-background border border-border rounded-md px-4 py-2.5 text-sm text-muted cursor-not-allowed"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-muted mb-1">Full Name</label>
                  <input 
                    type="text" 
                    value={profile.name}
                    onChange={e => setProfile({...profile, name: e.target.value})}
                    className="w-full bg-background border border-border rounded-md px-4 py-2.5 text-sm focus:border-foreground outline-none transition-colors"
                  />
                </div>
              </div>
            </div>

            <div className="p-6 border border-border bg-card rounded-xl">
              <div className="flex items-center gap-2 mb-4">
                <Key className="w-5 h-5 text-accent" />
                <h2 className="text-lg font-semibold">API Integrations</h2>
              </div>
              <p className="text-xs text-muted mb-6">Keys are stored securely and never exposed to the frontend.</p>
              
              <div className="grid gap-6">
                <div>
                  <label className="block text-sm font-medium text-muted mb-1">OpenAI API Key</label>
                  <div className="flex items-center gap-2">
                    <input 
                      type="password" 
                      placeholder={hasOpenAIKey ? "•••••••••••••••••••••••••••• (Key is set)" : "sk-..."}
                      value={profile.openai_api_key}
                      onChange={e => setProfile({...profile, openai_api_key: e.target.value})}
                      className="flex-1 bg-background border border-border rounded-md px-4 py-2.5 text-sm focus:border-foreground outline-none transition-colors"
                    />
                  </div>
                  <p className="text-xs text-muted mt-1">Used for AI Copilot and Auto-fixes. Requires GPT-4 access.</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-muted mb-1">GitHub Personal Access Token</label>
                  <div className="flex items-center gap-2">
                    <input 
                      type="password" 
                      placeholder={hasGitHubToken ? "•••••••••••••••••••••••••••• (Token is set)" : "ghp_..."}
                      value={profile.github_access_token}
                      onChange={e => setProfile({...profile, github_access_token: e.target.value})}
                      className="flex-1 bg-background border border-border rounded-md px-4 py-2.5 text-sm focus:border-foreground outline-none transition-colors"
                    />
                  </div>
                  <p className="text-xs text-muted mt-1">Used to post review comments and open PRs. Needs `repo` scope.</p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4">
              <div className="text-sm font-medium">
                {message.text && (
                  <span className={message.type === "success" ? "text-green-500" : "text-red-500"}>
                    {message.text}
                  </span>
                )}
              </div>
              <button 
                type="submit" 
                disabled={saving}
                className="px-6 py-2.5 bg-foreground text-background font-semibold rounded-md hover:bg-foreground/90 transition-colors disabled:opacity-50 flex items-center gap-2 text-sm"
              >
                <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save Changes"}
              </button>
            </div>
          </form>
        )}
      </main>
    </div>
  );
}
