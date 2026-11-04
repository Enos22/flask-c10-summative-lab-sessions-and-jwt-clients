import React, { useEffect, useState } from "react";
import { apiRequest } from "../api";
import Box from "../styles/Box";

function ViewDoses() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    apiRequest("/api/reports/daily")
      .then((result) => {
        if (active) setReport(result);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  if (loading) return <p>Loading today's doses…</p>;
  if (error) return <p role="alert">{error}</p>;

  const doses = [
    ...(report.pending || []),
    ...(report.taken || []),
    ...(report.missed || []),
  ].sort((left, right) =>
    left.scheduled_time.localeCompare(right.scheduled_time)
  );

  return (
    <section className="doses-container">
      <h2>Doses for {report.date}</h2>

      {doses.length === 0 ? (
        <p className="empty-state">No doses scheduled for today.</p>
      ) : (
        <div className="doses-grid">
          {doses.map((dose) => (
            <Box className="dose-card" key={dose.dose_id}>
              <div className="dose-icon"></div>

              <h3>
                {dose.medication_name} — {dose.dosage}
              </h3>

              <p>
                <strong>Scheduled:</strong>{" "}
                {new Date(dose.scheduled_time).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                <span
                  className={`dose-status ${dose.status.toLowerCase()}`}
                >
                  {dose.status}
                </span>
              </p>

              {dose.taken_at && (
                <p>
                  <strong>Taken at:</strong>{" "}
                  {new Date(dose.taken_at).toLocaleString()}
                </p>
              )}
            </Box>
          ))}
        </div>
      )}
    </section>
  );
}

export default ViewDoses;