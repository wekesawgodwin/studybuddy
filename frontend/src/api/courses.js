const BASE_URL = import.meta.env.VITE_API_URL;

export async function getCourses(token) {
  const res = await fetch(`${BASE_URL}/courses/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch courses");
  return res.json();
}

export async function getCourse(token, courseId) {
  const res = await fetch(`${BASE_URL}/courses/${courseId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch course");
  return res.json();
}

export async function getTopic(token, topicId) {
  const res = await fetch(`${BASE_URL}/topics/${topicId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch topic");
  return res.json();
}

/**
 * Uploads a markdown file as topic content.
 * Do NOT set Content-Type manually — FormData sets it automatically.
 */
export async function uploadTopicContent(token, topicId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/topics/${topicId}/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to upload file");
  }

  return res.json();
}