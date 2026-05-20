import { useNavigate } from "react-router-dom";

export default function LearningPath({ modules }) {
  if (!modules || modules.length === 0) {
    return <p style={styles.empty}>No modules available yet.</p>;
  }

  return (
    <div style={styles.container}>
      {modules.map((module, moduleIndex) => (
        <div key={module.id} style={styles.module}>
          <div style={styles.moduleHeader}>
            <span style={styles.moduleIndex}>Module {moduleIndex + 1}</span>
            <h3 style={styles.moduleTitle}>{module.title}</h3>
            {module.description && (
              <p style={styles.moduleDescription}>{module.description}</p>
            )}
          </div>

          {module.submodules.length === 0 ? (
            <p style={styles.emptyInner}>No submodules yet.</p>
          ) : (
            module.submodules.map((submodule, subIndex) => (
              <SubModuleSection
                key={submodule.id}
                submodule={submodule}
                subIndex={subIndex}
              />
            ))
          )}
        </div>
      ))}
    </div>
  );
}

function SubModuleSection({ submodule, subIndex }) {
  return (
    <div style={styles.submodule}>
      <div style={styles.submoduleHeader}>
        <div style={styles.submoduleIndex}>{subIndex + 1}</div>
        <div>
          <p style={styles.submoduleTitle}>{submodule.title}</p>
          {submodule.description && (
            <p style={styles.submoduleDescription}>{submodule.description}</p>
          )}
        </div>
      </div>

      {submodule.topics.length === 0 ? (
        <p style={styles.emptyInner}>No topics yet.</p>
      ) : (
        <div style={styles.topicList}>
          {submodule.topics.map((topic, index) => (
            <TopicRow key={topic.id} topic={topic} index={index} />
          ))}
        </div>
      )}
    </div>
  );
}

function TopicRow({ topic, index }) {
  const navigate = useNavigate();

  return (
    <div style={styles.topicRow} onClick={() => navigate(`/topics/${topic.id}`)}>
      <div style={styles.topicNumber}>{index + 1}</div>
      <div style={styles.topicContent}>
        <span style={styles.topicTitle}>{topic.title}</span>
        <span style={styles.topicFilename}>
          {topic.has_content
            ? `📄 ${topic.content_filename || "Markdown uploaded"}`
            : "⚠ No content yet"}
        </span>
      </div>
      <div style={styles.topicMeta}>
        {topic.mastery_required && (
          <span style={styles.masteryBadge}>Mastery</span>
        )}
        <span style={styles.arrow}>→</span>
      </div>
    </div>
  );
}

const styles = {
  container: { display: "flex", flexDirection: "column", gap: "24px" },
  module: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: "12px",
    overflow: "hidden",
  },
  moduleHeader: { padding: "20px 24px", background: "#4f46e5" },
  moduleIndex: {
    fontSize: "11px", fontWeight: "700", color: "#a5b4fc",
    textTransform: "uppercase", letterSpacing: "1px",
  },
  moduleTitle: { margin: "4px 0", fontSize: "18px", fontWeight: "700", color: "#fff" },
  moduleDescription: { margin: 0, color: "#c7d2fe", fontSize: "13px" },
  submodule: { borderBottom: "1px solid #f3f4f6" },
  submoduleHeader: {
    display: "flex", alignItems: "flex-start", gap: "12px",
    padding: "16px 24px", background: "#f9fafb",
    borderBottom: "1px solid #f3f4f6",
  },
  submoduleIndex: {
    width: "24px", height: "24px", borderRadius: "50%",
    background: "#e0e7ff", color: "#4f46e5",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "12px", fontWeight: "700", flexShrink: 0,
  },
  submoduleTitle: { margin: 0, fontSize: "15px", fontWeight: "600", color: "#1a1a1a" },
  submoduleDescription: { margin: "2px 0 0", fontSize: "12px", color: "#666" },
  topicList: { padding: "4px 0" },
  topicRow: {
    display: "flex", alignItems: "center",
    padding: "12px 24px 12px 36px",
    cursor: "pointer", borderBottom: "1px solid #f9fafb", gap: "12px",
  },
  topicNumber: {
    width: "28px", height: "28px", borderRadius: "50%",
    background: "#f3f4f6", color: "#6b7280",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "12px", fontWeight: "700", flexShrink: 0,
  },
  topicContent: { flex: 1, display: "flex", flexDirection: "column", gap: "2px" },
  topicTitle: { fontSize: "14px", fontWeight: "600", color: "#1a1a1a" },
  topicFilename: { fontSize: "12px", color: "#9ca3af" },
  topicMeta: { display: "flex", alignItems: "center", gap: "8px" },
  masteryBadge: {
    background: "#fef3c7", color: "#92400e",
    padding: "2px 6px", borderRadius: "999px", fontSize: "10px", fontWeight: "600",
  },
  arrow: { color: "#9ca3af" },
  empty: { color: "#9ca3af", padding: "16px", margin: 0 },
  emptyInner: { color: "#9ca3af", padding: "12px 24px", margin: 0, fontSize: "13px" },
};