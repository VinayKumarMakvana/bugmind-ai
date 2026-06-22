"use client";

import Link from "next/link";
import { motion, Variants } from "framer-motion";
import { Shield, Zap, Code2, ArrowRight } from "lucide-react";

export default function Home() {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground selection:bg-foreground selection:text-background">
      <nav className="fixed w-full z-50 border-b border-border/50 bg-background/80 backdrop-blur-md px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-foreground rounded-md flex items-center justify-center">
            <Shield className="w-5 h-5 text-background" />
          </div>
          <span className="text-xl font-bold tracking-tight">BugMind</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-sm font-medium hover:text-muted transition-colors">
            Dashboard
          </Link>
          <a href={`${process.env.NEXT_PUBLIC_API_URL || "https://bugmind-ai.onrender.com/api/v1"}/github/login`} className="px-5 py-2 bg-foreground text-background rounded-md text-sm font-semibold hover:bg-foreground/90 transition-colors flex items-center gap-2">
            <Code2 className="w-4 h-4" />
            Connect GitHub
          </a>
        </div>
      </nav>

      <main className="flex-1 flex flex-col items-center justify-center pt-32 pb-16 px-6 lg:pt-48 lg:pb-32 text-center">
        <motion.div 
          className="max-w-4xl w-full flex flex-col items-center"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={itemVariants} className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border text-xs font-medium mb-8 bg-card">
            <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
            BugMind Engine v2.0 is Live
          </motion.div>
          
          <motion.h1 variants={itemVariants} className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
            The Ultimate <br />
            <span className="text-muted">AI Code Reviewer</span>
          </motion.h1>
          
          <motion.p variants={itemVariants} className="text-lg md:text-xl text-muted max-w-2xl mx-auto mb-12 leading-relaxed">
            BugMind AI doesn't just find bugs. It understands your entire codebase context, detects critical vulnerabilities, and generates optimized fixes in seconds.
          </motion.p>

          <motion.div variants={itemVariants} className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/dashboard" className="px-8 py-3.5 bg-foreground text-background font-semibold rounded-md hover:bg-foreground/90 transition-colors flex items-center gap-2">
              Start Free Trial <ArrowRight className="w-4 h-4" />
            </Link>
            <button className="px-8 py-3.5 bg-card border border-border text-foreground font-semibold rounded-md hover:bg-card/80 transition-colors flex items-center gap-2">
              <Code2 className="w-4 h-4" /> View Documentation
            </button>
          </motion.div>

          <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl text-left mt-24">
            {[
              { icon: Code2, title: "Context-Aware", desc: "Embeds your entire repo in ChromaDB for deep contextual understanding." },
              { icon: Zap, title: "Instant Auto-Fixes", desc: "Generates precise patches and pushes them directly to your PR." },
              { icon: Shield, title: "Zero False Positives", desc: "Combines semantic analysis with LLMs to eliminate noisy alerts." }
            ].map((feature, i) => (
              <motion.div key={i} variants={itemVariants} className="p-6 rounded-xl border border-border bg-card/30 hover:bg-card/50 transition-colors">
                <div className="w-10 h-10 rounded-lg bg-foreground/5 flex items-center justify-center mb-4 text-foreground border border-border/50">
                  <feature.icon className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
}
