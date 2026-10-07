"use client";
import { useState, useEffect, useCallback } from "react";
import { Wand2, LayoutDashboard, Clock, CheckCircle2, AlertCircle } from "lucide-react";

// 1. We added this TypeScript Interface to fix the "any" error
interface Post {
  id: string;
  topic: string;
  status: string;
}

export default function Dashboard() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchPosts = useCallback(async () => {
    try {
      const response = await fetch("http://localhost:8000/api/content");
      const data = await response.json();
      setPosts(data);
    } catch (error) {
      console.error("Failed to fetch posts:", error);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchPosts();
  }, [fetchPosts]);

  const generateContent = async () => {
    if (!topic) return;
    setLoading(true);
    try {
      await fetch("http://localhost:8000/api/content", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, title: "New AI Post" }),
      });
      setTopic("");
      fetchPosts(); 
    } catch (error) {
      console.error("Failed to generate content:", error);
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-[#0a0f1d] text-white p-8 md:p-16 relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-cyan-500/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-6xl mx-auto relative z-10">
        <header className="mb-16 flex items-center justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-3">
              Hades<span className="text-cyan-400">Reality</span>
            </h1>
            <p className="text-slate-400 text-lg flex items-center gap-2">
              <LayoutDashboard className="w-5 h-5" /> ContentOps Engine
            </p>
          </div>
        </header>

        <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-3xl mb-12 shadow-2xl transition-all duration-300 hover:border-cyan-500/30">
          <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <Wand2 className="w-6 h-6 text-cyan-400" /> AI Content Generator
          </h2>
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Why B2B SaaS needs automation in 2026..."
              className="flex-1 bg-black/40 border border-white/10 rounded-xl px-6 py-4 text-white focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition-all placeholder:text-slate-500 text-lg"
            />
            <button
              onClick={generateContent}
              disabled={loading || !topic}
              className="bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed text-[#0a0f1d] font-bold py-4 px-10 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 text-lg shadow-[0_0_20px_rgba(0,255,255,0.3)] hover:shadow-[0_0_30px_rgba(0,255,255,0.5)]"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-[#0a0f1d] border-t-transparent rounded-full animate-spin" />
                  Generating...
                </span>
              ) : (
                "Generate Post"
              )}
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-semibold flex items-center gap-2">
            <Clock className="w-6 h-6 text-slate-400" /> Review Queue
          </h2>
          <span className="bg-cyan-500/10 text-cyan-400 px-4 py-1 rounded-full text-sm font-medium border border-cyan-500/20">
            {posts.length} Posts
          </span>
        </div>

        <div className="grid gap-6">
          {posts.map((post) => (
            <div
              key={post.id}
              className="group bg-white/5 backdrop-blur-md border border-white/10 p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6 transition-all duration-300 hover:bg-white/10 hover:border-cyan-500/50 cursor-default"
            >
              <div className="flex-1">
                <h3 className="font-semibold text-xl mb-2 text-white group-hover:text-cyan-400 transition-colors">
                  {post.topic}
                </h3>
                <div className="flex items-center gap-3">
                  {post.status === "FAILED" ? (
                    <span className="flex items-center gap-1 text-sm text-red-400 bg-red-400/10 px-3 py-1 rounded-full">
                      <AlertCircle className="w-4 h-4" /> Failed
                    </span>
                  ) : post.status === "GENERATING" ? (
                    <span className="flex items-center gap-1 text-sm text-yellow-400 bg-yellow-400/10 px-3 py-1 rounded-full">
                      <Clock className="w-4 h-4" /> Generating
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-sm text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full">
                      <CheckCircle2 className="w-4 h-4" /> Ready for Review
                    </span>
                  )}
                  <span className="text-sm text-slate-500">ID: {post.id.substring(0, 8)}...</span>
                </div>
              </div>
              <button
                disabled={post.status !== "PENDING_REVIEW"}
                className="w-full md:w-auto border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500 hover:text-[#0a0f1d] disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-cyan-400 px-8 py-3 rounded-xl font-medium transition-all duration-300"
              >
                Review Content
              </button>
            </div>
          ))}

          {posts.length === 0 && (
            <div className="text-center py-20 bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl border-dashed">
              <p className="text-slate-400 text-lg">No posts in the queue.</p>
              <p className="text-slate-500 text-sm mt-2">Use the generator above to create your first post.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
