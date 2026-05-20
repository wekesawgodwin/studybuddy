import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getTopic } from "../api/courses";

export default function TopicPage() {
  const { topicId } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();

  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getTopic(token, topicId)
      .then(setTopic)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [topicId, token]);

  if (loading) return <div style={styles.status}>Loading topic...</div>;

  if (error) return (
    <div style={styles.page}>
      <p style={styles.error}>Failed to load topic: {error}</p>
      <button onClick={() => navigate(-1)} style={styles.backButton}>← Go back</button>
    </div>
  );

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <button onClick={() => navigate(-1)} style={styles.backLink}>← Back</button>
      </header>

      <div style={styles.hero}>
        <div style={styles.heroContent}>
          <h1 style={styles.topicTitle}>{topic.title}</h1>
          {topic.content_filename && (
            <p style={styles.filename}>📄 {topic.content_filename}</p>
          )}
        </div>
      </div>

      <main style={styles.main}>
        {topic.content ? (
          <div style={styles.markdownContainer}>
            {/*
              Renders markdown as preformatted text.
              Install react-markdown for proper rendering:
                npm install react-markdown
              Then replace the pre tag with:
                <ReactMarkdown>{topic.content}</ReactMarkdown>
            */}
            <pre style={styles.markdownContent}>{topic.content}</pre>
          </div>
        ) : (
          <div style={styles.noContent}>
            <p>⚠ No content has been uploaded for this topic yet.</p>
          </div>
        )}
      </main>
    </div>
  );
}

const styles = {
  page: { minHeight: "100vh", background: "#f9fafb" },
  header: { background: "#fff", borderBottom: "1px solid #e5e7eb", padding: "0 24px" },
  backLink: {
    background: "none", border: "none", color: "#4f46e5",
    cursor: "pointer", fontSize: "14px", fontWeight: "600",
    padding: "20px 0", display: "block",
  },
  hero: { background: "#1e1b4b", padding: "32px 24px" },
  heroContent: { maxWidth: "800px", margin: "0 auto" },
  topicTitle: { margin: "0 0 8px 0", fontSize: "26px", fontWeight: "800", color: "#fff" },
  filename: { margin: 0, color: "#a5b4fc", fontSize: "13px" },
  main: { maxWidth: "800px", margin: "0 auto", padding: "32px 24px" },
  markdownContainer: {
    background: "#fff", border: "1px solid #e5e7eb",
    borderRadius: "12px", padding: "32px",
  },
  markdownContent: {
    margin: 0, fontFamily: "inherit", fontSize: "15px",
    lineHeight: "1.8", color: "#1a1a1a",
    whiteSpace: "pre-wrap", wordBreak: "break-word",
  },
  noContent: {
    background: "#fff", border: "1px solid #fbbf24",
    borderRadius: "12px", padding: "32px",
    textAlign: "center", color: "#92400e",
  },
  status: {
    display: "flex", height: "100vh",
    alignItems: "center", justifyContent: "center", color: "#9ca3af",
  },
  error: { color: "#dc2626", padding: "24px" },
  backButton: {
    margin: "0 24px", padding: "8px 16px",
    border: "1px solid #e5e7eb", borderRadius: "8px",
    cursor: "pointer", background: "none",
  },
};