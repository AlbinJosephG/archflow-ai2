
import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [description, setDescription] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [session, setSession] = useState(null);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [recommendations, setRecommendations] = useState({});
  const [readiness, setReadiness] = useState(null);
  const [completed, setCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [customValues, setCustomValues] = useState({});
  

  // --------------------------------------------------
  // API RESPONSE HANDLER
  // --------------------------------------------------

  const handleResponse = async (response) => {
    let data;

    try {
      data = await response.json();
    } catch {
      throw new Error("Invalid response received from the server.");
    }

    if (!response.ok) {
      throw new Error(
        data.detail || data.message || "Something went wrong."
      );
    }

    return data;
  };

  // --------------------------------------------------
  // UPDATE SESSION STATE
  // --------------------------------------------------

  const updateSessionState = (data) => {
    const updatedSession = data.session;

    if (updatedSession) {
      setSession(updatedSession);
      setSessionId(updatedSession.session_id);
      setRecommendations(updatedSession.recommendations || {});
    }

    if (data.question !== undefined) {
      setQuestion(data.question);
    }

    if (data.completed !== undefined) {
      setCompleted(data.completed);
    }

    if (data.readiness) {
      setReadiness(data.readiness);
    }
  };

  // --------------------------------------------------
  // STEP 1: CREATE ROOM SESSION
  // --------------------------------------------------

  const createSession = async () => {
    if (!description.trim()) {
      setError("Please describe the room you want to design.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/room/session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          description: description.trim(),
        }),
      });

      const data = await handleResponse(response);

      updateSessionState(data);

      // Fetch current room readiness.
      const readinessResponse = await fetch(
        `${API_URL}/room/session/${data.session.session_id}/readiness`
      );

      const readinessData = await handleResponse(readinessResponse);
      setReadiness(readinessData);

      setAnswer("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // STEP 2: SUBMIT ANSWER
  // --------------------------------------------------

  const submitAnswer = async () => {
    if (!answer.trim() || !sessionId) {
      setError("Please enter your answer.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/room/session/${sessionId}/answer`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            answer: answer.trim(),
          }),
        }
      );

      const data = await handleResponse(response);

      updateSessionState(data);
      setAnswer("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // STEP 3: ACCEPT OR REJECT RECOMMENDATION
  // --------------------------------------------------

  const handleRecommendation = async (field, action) => {
    if (!sessionId) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/room/session/${sessionId}/recommendations/${field}/${action}`,
        {
          method: "POST",
        }
      );

      const data = await handleResponse(response);

      updateSessionState(data);

      // Refresh readiness after the decision.
      const readinessResponse = await fetch(
        `${API_URL}/room/session/${sessionId}/readiness`
      );

      const readinessData = await handleResponse(readinessResponse);
      setReadiness(readinessData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

const handleCustomValue = async (field) => {
  const value = customValues[field]?.trim();

  if (!value) {
    setError(`Please enter a value for ${field.replaceAll("_", " ")}.`);
    return;
  }

  if (!sessionId) return;

  setLoading(true);
  setError("");

  try {
    const response = await fetch(
      `${API_URL}/room/session/${sessionId}/recommendations/${field}/custom`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          answer: value,
        }),
      }
    );

    const data = await handleResponse(response);

    updateSessionState(data);

    setReadiness(data.readiness);

    setCustomValues((previous) => ({
      ...previous,
      [field]: "",
    }));

  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

  // --------------------------------------------------
  // STEP 4: START NEW SESSION
  // --------------------------------------------------

  const resetSession = () => {
    setDescription("");
    setSessionId(null);
    setSession(null);
    setQuestion(null);
    setAnswer("");
    setRecommendations({});
    setCustomValues({});
    setReadiness(null);
    setCompleted(false);
    setError("");
  };

  // --------------------------------------------------
  // HELPER: FORMAT FIELD NAMES
  // --------------------------------------------------

  const formatField = (field) => {
    return field
      .replaceAll("_", " ")
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  const styles = {
    page: {
      minHeight: "100vh",
      background: "#0b1020",
      color: "#f1f5f9",
      padding: "40px 20px",
      fontFamily: "Inter, Arial, sans-serif",
    },
    container: {
      maxWidth: "900px",
      margin: "0 auto",
    },
    card: {
      background: "#151d30",
      border: "1px solid #273449",
      borderRadius: "14px",
      padding: "24px",
      marginBottom: "20px",
    },
    textarea: {
      width: "100%",
      boxSizing: "border-box",
      background: "#0b1222",
      color: "#f1f5f9",
      border: "1px solid #334155",
      borderRadius: "8px",
      padding: "14px",
      fontSize: "15px",
      resize: "vertical",
      outline: "none",
    },
    button: {
      background: "#6366f1",
      color: "white",
      border: "none",
      borderRadius: "8px",
      padding: "11px 18px",
      cursor: "pointer",
      fontWeight: "600",
    },
    secondaryButton: {
      background: "#263449",
      color: "#e2e8f0",
      border: "1px solid #475569",
      borderRadius: "8px",
      padding: "10px 16px",
      cursor: "pointer",
    },
    heading: {
      color: "#f8fafc",
      marginTop: 0,
    },
    muted: {
      color: "#94a3b8",
    },
    error: {
      background: "#451a24",
      color: "#fca5a5",
      border: "1px solid #7f1d1d",
      padding: "12px",
      borderRadius: "8px",
      marginBottom: "20px",
    },
    code: {
      background: "#0b1222",
      color: "#cbd5e1",
      padding: "14px",
      borderRadius: "8px",
      overflowX: "auto",
      fontSize: "13px",
      lineHeight: 1.6,
    },
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>

        {/* HEADER */}

        <header style={{ marginBottom: "35px" }}>
          <h1 style={{ ...styles.heading, fontSize: "32px" }}>
            ArchFlow AI
          </h1>

          <p style={styles.muted}>
            AI-powered single-room architectural design assistant.
          </p>
        </header>

        {/* ERROR */}

        {error && (
          <div style={styles.error}>
            {error}
          </div>
        )}

        {/* CREATE ROOM */}

        {!sessionId && (
          <section style={styles.card}>
            <h2 style={styles.heading}>
              Describe Your Room
            </h2>

            <p style={styles.muted}>
              Tell us about your room, its dimensions, design preferences,
              materials and furniture.
            </p>

            <textarea
              style={styles.textarea}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Example: I want a modern living room with dimensions of 14 feet width, 18 feet length and 10 feet height. I prefer minimalist interiors, wooden flooring, warm lighting and a large sofa."
              rows={6}
            />

            <button
              style={{ ...styles.button, marginTop: "16px" }}
              onClick={createSession}
              disabled={loading}
            >
              {loading ? "Creating Room..." : "Start Room Design"}
            </button>
          </section>
        )}

        {/* ROOM SESSION */}

        {sessionId && (
          <>
            <section style={styles.card}>
              <h2 style={styles.heading}>
                Room Design Session
              </h2>

              <p style={styles.muted}>
                Session ID: {sessionId}
              </p>

              <p style={styles.muted}>
                Room Type: {session?.requirements?.room_type || "Not specified"}
              </p>
            </section>

            {/* ADAPTIVE QUESTION */}

            {question && (
              <section style={styles.card}>
                <h2 style={styles.heading}>
                  Room Requirements
                </h2>

                <h3>{question.question}</h3>

                {question.priority && (
                  <p style={styles.muted}>
                    Priority: {question.priority}
                  </p>
                )}

                {question.reason && (
                  <p style={styles.muted}>
                    {question.reason}
                  </p>
                )}

                {question.options?.length > 0 && (
                  <div style={{ marginBottom: "15px" }}>
                    {question.options.map((option) => (
                      <button
                        key={option.value}
                        style={{
                          ...styles.secondaryButton,
                          margin: "5px",
                          borderColor:
                            answer === String(option.value)
                              ? "#818cf8"
                              : "#475569",
                        }}
                        onClick={() => setAnswer(String(option.value))}
                        disabled={loading}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                )}

                <textarea
                  style={styles.textarea}
                  value={answer}
                  onChange={(event) => setAnswer(event.target.value)}
                  placeholder="Enter your answer..."
                  rows={3}
                />

                <button
                  style={{ ...styles.button, marginTop: "15px" }}
                  onClick={submitAnswer}
                  disabled={loading || !answer.trim()}
                >
                  {loading ? "Processing..." : "Submit Answer"}
                </button>
              </section>
            )}

            {/* AI RECOMMENDATIONS */}

            {Object.keys(recommendations).length > 0 && (
              <section style={styles.card}>
                <h2 style={styles.heading}>
                  AI Design Recommendations
                </h2>

                <p style={styles.muted}>
                  Review each suggestion and accept or reject it.
                </p>

                {Object.entries(recommendations).map(([field, item]) => (
                  <div
                    key={field}
                    style={{
                      background: "#0b1222",
                      border: "1px solid #334155",
                      borderRadius: "10px",
                      padding: "16px",
                      marginTop: "14px",
                    }}
                  >
                    <h3 style={{ marginTop: 0 }}>
                      {formatField(field)}
                    </h3>

                    <p>
  <strong>
    {item.status === "superseded" ? "Your value:" : "Suggestion:"}
  </strong>{" "}
  {(() => {
    const value =
      item.status === "superseded"
        ? session?.requirements?.[field]
        : item.value;

    return Array.isArray(value)
      ? value.join(", ")
      : String(value ?? "Not specified");
  })()}
</p>

                    <p style={styles.muted}>
                      {item.reason}
                    </p>

                    <p style={styles.muted}>
                      Status: {item.status}
                    </p>

                    
{item.status === "pending" && (
  <div style={{ marginTop: "15px" }}>

    <label
      style={{
        display: "block",
        marginBottom: "8px",
        color: "#cbd5e1",
        fontSize: "14px",
      }}
    >
      Enter your own value
    </label>

    <input
      type={
        field === "door_count" || field === "window_count"
          ? "number"
          : "text"
      }
      min={
        field === "door_count" || field === "window_count"
          ? "0"
          : undefined
      }
      step="1"
      value={customValues[field] || ""}
      onChange={(event) =>
        setCustomValues((previous) => ({
          ...previous,
          [field]: event.target.value,
        }))
      }
      placeholder={
        field === "furniture"
          ? "Example: L-shaped sofa, bookshelf, TV unit"
          : field === "door_count"
          ? "Enter number of doors"
          : field === "window_count"
          ? "Enter number of windows"
          : `Enter your preferred ${formatField(field).toLowerCase()}`
      }
      style={{
        width: "100%",
        boxSizing: "border-box",
        padding: "12px",
        borderRadius: "8px",
        border: "1px solid #475569",
        background: "#151d30",
        color: "#f1f5f9",
        marginBottom: "12px",
      }}
    />

    <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>

      <button
        style={styles.button}
        onClick={() => handleCustomValue(field)}
        disabled={loading || !customValues[field]?.trim()}
      >
        Use My Value
      </button>

      <button
        style={styles.secondaryButton}
        onClick={() => handleRecommendation(field, "accept")}
        disabled={loading}
      >
        Accept Suggestion
      </button>

      <button
        style={styles.secondaryButton}
        onClick={() => handleRecommendation(field, "reject")}
        disabled={loading}
      >
        Reject
      </button>

    </div>
  </div>
)}

                  </div>
                ))}
              </section>
            )}

            {/* ROOM READINESS */}

            {readiness && (
              <section style={styles.card}>
                <h2 style={styles.heading}>
                  Room Readiness
                </h2>

                <p>
                  Brief Completed:{" "}
                  <strong>
                    {readiness.brief_completed ? "Yes" : "No"}
                  </strong>
                </p>

                <p>
                  Scene Ready:{" "}
                  <strong>
                    {readiness.scene_ready ? "Yes" : "No"}
                  </strong>
                </p>

                {readiness.missing_core_fields?.length > 0 && (
                  <div>
                    <h4>Missing Core Requirements</h4>
                    <ul>
                      {readiness.missing_core_fields.map((field) => (
                        <li key={field}>{formatField(field)}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {readiness.missing_scene_fields?.length > 0 && (
                  <div>
                    <h4>Missing Scene Requirements</h4>
                    <ul>
                      {readiness.missing_scene_fields.map((field) => (
                        <li key={field}>{formatField(field)}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {readiness.unconfirmed_scene_fields?.length > 0 && (
                  <div>
                    <h4>Unconfirmed Recommendations</h4>
                    <ul>
                      {readiness.unconfirmed_scene_fields.map((field) => (
                        <li key={field}>{formatField(field)}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {readiness.scene_ready && (
                  <p style={{ color: "#4ade80", fontWeight: "600" }}>
                    Room requirements are ready for scene generation.
                  </p>
                )}
              </section>
            )}

            {/* CURRENT REQUIREMENTS */}

            {session?.requirements && (
              <section style={styles.card}>
                <h2 style={styles.heading}>
                  Current Room Requirements
                </h2>

                <pre style={styles.code}>
                  {JSON.stringify(session.requirements, null, 2)}
                </pre>
              </section>
            )}

            {/* RESET */}

            <button
              style={styles.secondaryButton}
              onClick={resetSession}
              disabled={loading}
            >
              Start New Room
            </button>
          </>
        )}

        {/* LOADING */}

        {loading && (
          <p style={{ ...styles.muted, marginTop: "20px" }}>
            Communicating with ArchFlow AI...
          </p>
        )}

      </div>
    </div>
  );
}

export default App;
