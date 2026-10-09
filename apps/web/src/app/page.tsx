"use client";
import { useState, useEffect, useCallback } from "react";
import {
  Wand2,
  LayoutDashboard,
  Clock,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

interface Post {
  id: string;
  topic: string;
  status: string;
}

export default function Dashboard() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);

  // New variables for our Review Pop-up
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [isReviewing, setIsReviewing] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  
  // New variables for AI Revisions
  const [feedback, setFeedback] = useState("");
  const [revisionLoading, setRevisionLoading] = useState(false);

  // New variable for Scheduling
  const [scheduledTime, setScheduledTime] = useState("");

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

  // 1. Fetch the exact image and caption when "Review" is clicked
  const handleReviewClick = async (postId: string) => {
    setIsReviewing(true); // Open the modal
    setSelectedPost(null); // Clear old data
    setScheduledTime(""); // Clear old time
    try {
      const res = await fetch(`http://localhost:8000/api/content/${postId}`);
      const data = await res.json();
      setSelectedPost(data);
    } catch (error) {
      console.error("Failed to fetch details:", error);
    }
  };

  // 2. Tell the database to Approve it!
  const approvePost = async () => {
    if (!selectedPost) return;
    setActionLoading(true);
    try {
      await fetch(
        `http://localhost:8000/api/content/${selectedPost.id}/approve`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ scheduled_time: scheduledTime || null }),
        },
      );
      setIsReviewing(false); // Close the modal
      fetchPosts(); // Refresh the list so it says APPROVED
    } catch (error) {
      console.error("Failed to approve:", error);
    }
    setActionLoading(false);
  };

  // 3. Ask the AI to revise the post!
  const revisePost = async () => {
    if (!selectedPost || !feedback) return;
    setRevisionLoading(true);
    try {
      await fetch(
        `http://localhost:8000/api/content/${selectedPost.id}/revise`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ feedback }),
        }
      );
      setFeedback("");
      // Re-fetch the post to see the new version!
      handleReviewClick(selectedPost.id);
    } catch (error) {
      console.error("Failed to revise:", error);
    }
    setRevisionLoading(false);
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
              {loading ? "Generating..." : "Generate Post"}
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
                  {post.status === "APPROVED" ? (
                    <span className="flex items-center gap-1 text-sm text-cyan-400 bg-cyan-400/10 px-3 py-1 rounded-full">
                      <CheckCircle2 className="w-4 h-4" /> Approved
                    </span>
                  ) : post.status === "PENDING_REVIEW" ? (
                    <span className="flex items-center gap-1 text-sm text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full">
                      <Clock className="w-4 h-4" /> Ready for Review
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-sm text-slate-400 bg-slate-400/10 px-3 py-1 rounded-full">
                      {post.status}
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleReviewClick(post.id)}
                disabled={post.status !== "PENDING_REVIEW"}
                className="w-full md:w-auto border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500 hover:text-[#0a0f1d] disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-cyan-400 px-8 py-3 rounded-xl font-medium transition-all duration-300"
              >
                Review Content
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* --- THE NEW REVIEW POP-UP MODAL --- */}
      {isReviewing && (
        <div className="fixed inset-0 bg-[#0a0f1d]/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-white/10 rounded-3xl w-full max-w-5xl shadow-2xl overflow-hidden flex flex-col md:flex-row min-h-[500px]">
            {/* Left side: Displays the Image */}
            <div className="w-full md:w-1/2 bg-black flex items-center justify-center p-8 border-r border-white/5 relative">
              {!selectedPost ? (
                <div className="w-10 h-10 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
              ) : selectedPost.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={selectedPost.image_url}
                  alt="Generated AI graphic"
                  className="w-full max-w-md h-auto rounded-xl shadow-[0_0_30px_rgba(0,255,255,0.15)]"
                />
              ) : (
                <div className="text-slate-500 text-center">
                  <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Image could not be loaded</p>
                </div>
              )}
            </div>

            {/* Right side: Displays Caption and Buttons */}
            <div className="w-full md:w-1/2 p-8 flex flex-col">
              <h2 className="text-3xl font-bold mb-6 text-white tracking-tight">
                Review Content
              </h2>

              {selectedPost ? (
                <>
                  <div className="mb-6 flex-1 flex flex-col">
                    <label className="text-xs text-cyan-400 font-bold mb-3 uppercase tracking-widest">
                      Generated Caption
                    </label>
                    <textarea
                      className="w-full flex-1 min-h-[150px] bg-black/40 border border-white/10 rounded-xl p-5 text-slate-300 text-lg leading-relaxed focus:outline-none focus:border-cyan-400 resize-none transition-colors"
                      defaultValue={selectedPost.caption}
                    />
                  </div>

                  <div className="mb-6 flex flex-col gap-2">
                     <label className="text-xs text-purple-400 font-bold uppercase tracking-widest flex items-center gap-2">
                      <Wand2 className="w-4 h-4" /> Ask AI to Revise
                    </label>
                    <div className="flex gap-2">
                      <input 
                        type="text"
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="e.g., Make it shorter, change color to red..."
                        className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-purple-400 text-sm"
                      />
                      <button
                        onClick={revisePost}
                        disabled={revisionLoading || !feedback}
                        className="bg-purple-500 hover:bg-purple-400 disabled:opacity-50 text-white font-bold px-6 rounded-xl transition-all shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                      >
                        {revisionLoading ? "Thinking..." : "Revise"}
                      </button>
                    </div>
                  </div>

                  <div className="mb-6 flex flex-col gap-2">
                    <label className="text-xs text-blue-400 font-bold uppercase tracking-widest flex items-center gap-2">
                      <Clock className="w-4 h-4" /> Schedule Post (Optional)
                    </label>
                    <input 
                      type="datetime-local" 
                      value={scheduledTime}
                      onChange={(e) => setScheduledTime(e.target.value)}
                      className="bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-400 text-sm w-full"
                    />
                  </div>

                  <div className="flex gap-4 mt-auto">
                    <button
                      onClick={() => setIsReviewing(false)}
                      className="flex-1 py-4 px-6 rounded-xl font-bold border border-white/10 hover:bg-white/5 text-slate-300 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={approvePost}
                      disabled={actionLoading}
                      className="flex-1 py-4 px-6 rounded-xl font-bold bg-cyan-500 text-[#0a0f1d] hover:bg-cyan-400 transition-all shadow-[0_0_15px_rgba(0,255,255,0.3)] disabled:opacity-50"
                    >
                      {actionLoading ? "Saving..." : (scheduledTime ? "Approve & Schedule" : "Approve & Publish Now")}
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <p className="text-slate-500">Loading post data...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
