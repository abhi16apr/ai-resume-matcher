"use client";
import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [resumeText, setResumeText] = useState("");
  const [jobText, setJobText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

  async function handleMatch() {
    setLoading(true);
    setResult(null);
    const form = new FormData();
    form.append("job_text", jobText);
    if (file) form.append("resume", file);
    else form.append("resume_text", resumeText);

    try {
      const { data } = await axios.post(`${apiBase}/match`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(data);
    } catch (err: any) {
      alert(err?.response?.data?.error ?? "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-6 max-w-3xl mx-auto space-y-5">
      <h1 className="text-2xl font-bold">AI Resume Matcher</h1>

      <section className="space-y-2">
        <label className="font-medium">Resume (upload or paste)</label>
        <input type="file" accept=".pdf,.docx,.txt"
               onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
        <textarea
          className="w-full border rounded p-2 h-28"
          placeholder="…or paste resume text"
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
        />
      </section>

      <section className="space-y-2">
        <label className="font-medium">Job Description</label>
        <textarea
          className="w-full border rounded p-2 h-32"
          placeholder="Paste JD here"
          value={jobText}
          onChange={(e) => setJobText(e.target.value)}
        />
      </section>

      <button
        onClick={handleMatch}
        disabled={loading}
        className="border px-4 py-2 rounded"
      >
        {loading ? "Scoring…" : "Get Match Score"}
      </button>

      {result && (
        <section className="border rounded p-4 space-y-2">
          <p><b>Score:</b> {result.score}</p>
          <p><b>Overlap:</b> {result.overlap?.join(", ")}</p>
          <p><b>Gaps:</b> {result.gaps?.join(", ")}</p>
        </section>
      )}
    </main>
  );
}
