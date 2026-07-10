"use client";

import Link from "next/link";
import Image from "next/image";
import { Shield, Zap, Code2, ArrowRight, Sparkles, Upload } from "lucide-react";
import { useState, useEffect } from "react";


export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setMounted(true);
      if (localStorage.getItem("token")) {
        setIsLoggedIn(true);
      }
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground relative overflow-hidden">
      {/* Background ambient glow elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-[#8ab4f8] opacity-[0.07] blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-[#c58af9] opacity-[0.05] blur-[120px] pointer-events-none" />

      <nav className="border-b border-white/5 bg-background/50 px-6 py-4 flex justify-between items-center sticky top-0 z-50 glass">
        <div className="flex items-center gap-3">
          <div className="relative w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center">
             <Image src="/logo.png" alt="BugMind Logo" fill className="object-cover" />
          </div>
          <span className="text-xl font-bold tracking-tight text-foreground">BugMind<span className="text-primary">.ai</span></span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/editor" className="text-sm font-medium hover:text-primary transition-colors">
            Try Web IDE
          </Link>
          {mounted ? (
            isLoggedIn ? (
              <Link href="/dashboard" className="px-5 py-2 bg-primary text-primary-foreground rounded-full text-sm font-medium hover:opacity-90 transition-all flex items-center gap-2 gemini-shadow hover-lift">
                Dashboard
              </Link>
            ) : (
              <Link href="/login" className="px-5 py-2 bg-foreground text-background rounded-full text-sm font-medium hover:bg-foreground/90 transition-all flex items-center gap-2 gemini-shadow hover-lift">
                Sign in
              </Link>
            )
          ) : (
            <div className="w-24 h-9"></div>
          )}
        </div>
      </nav>

      <main className="flex-1 flex flex-col items-center pt-24 pb-16 px-6 max-w-5xl mx-auto w-full text-center relative z-10">
        
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 text-xs font-medium mb-12 glass gemini-shadow animate-float">
          <Sparkles className="w-3.5 h-3.5 text-primary" />
          <span className="gemini-gradient-text font-semibold">BugMind AI</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 text-foreground max-w-4xl leading-[1.1]">
          Write code. <br/><span className="gemini-gradient-text">We&apos;ll fix the bugs.</span>
        </h1>
        
        <p className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-14 leading-relaxed font-light">
          The cleanest AI-powered Web IDE. Paste your code and receive instant, precise analysis and bug-free solutions with complete guidance.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full max-w-xl mb-16">
          <Link href="/editor" className="w-full sm:w-1/2 py-4 bg-foreground text-background font-semibold rounded-full hover:scale-105 transition-all duration-300 gemini-shadow flex items-center justify-center gap-2 group">
            Launch Web IDE 
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1.5 transition-transform" />
          </Link>
          <Link href="/dashboard" className="w-full sm:w-1/2 py-4 bg-card border border-border text-foreground font-semibold rounded-full hover:border-primary transition-all duration-300 hover:scale-105 flex items-center justify-center gap-2 group glass">
            <Upload className="w-5 h-5 group-hover:-translate-y-1 transition-transform text-primary" />
            Upload Code
          </Link>
        </div>



        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
          {[
            { icon: Code2, title: "Monaco Editor", desc: "A robust coding environment powered by the same engine as VS Code." },
            { icon: Zap, title: "Real-time AI", desc: "Instant semantic analysis streams guidance directly to your screen." },
            { icon: Shield, title: "Secure & Native", desc: "Authenticate securely. Your code is processed entirely in memory." }
          ].map((feature, i) => (
            <div key={i} className="p-8 rounded-3xl glass border border-white/5 hover-lift transition-all group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/20 rounded-full blur-3xl -mr-10 -mt-10 transition-opacity opacity-0 group-hover:opacity-100" />
              <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mb-6 text-foreground group-hover:text-primary transition-colors border border-white/5">
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-foreground tracking-tight">{feature.title}</h3>
              <p className="text-sm text-muted leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
