import React, { useEffect, useState } from "react";
import { apiRequest } from "../api";
import Box from "../styles/Box";

const editableFields = [
  "name",
  "dosage",
  "instructions",
  "start_date",
  "end_date",
];

function ViewMedications() {
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [draft, setDraft] = useState(null);

  useEffect(() => {
    let active = true;

    apiRequest("/api/medications/getmedications")
      .then((result) => {
        if (active) setMedications(result.medications || []);
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

  function startEditing(medication) {
    setEditingId(medication.id);

    setDraft({
      ...medication,
      instructions: medication.instructions || "",
      start_date: medication.start_date || "",
      end_date: medication.end_date || "",
    });
  }

  async function saveMedication(event) {
    event.preventDefault();
    setError("");

    try {
      const result = await apiRequest(
        `/api/medications/update/${editingId}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            ...draft,
            instructions: draft.instructions || null,
            end_date: draft.end_date || null,
          }),
        }
      );

      setMedications((current) =>
        current.map((item) =>
          item.id === editingId ? result.medication : item
        )
      );

      setEditingId(null);
      setDraft(null);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  if (loading) return <p>Loading medications…</p>;

  return (
    <section className="medications-container">
      <h2>My Medications</h2>

      {error && <p role="alert">{error}</p>}

      {medications.length === 0 ? (
        !error && <p className="empty-state">No medications found.</p>
      ) : (
        <div className="medication-grid">
          {medications.map((medication) => (
            <Box className="medication-card" key={medication.id}>
              {editingId === medication.id ? (
                <form onSubmit={saveMedication}>
                  <h3>Edit Medication</h3>

                  {editableFields.map((field) => (
                    <label key={field}>
                      {field === "start_date"
                        ? "Start date"
                        : field === "end_date"
                        ? "End date"
                        : field[0].toUpperCase() + field.slice(1)}

                      {field === "instructions" ? (
                        <textarea
                          value={draft[field]}
                          onChange={(event) =>
                            setDraft({
                              ...draft,
                              [field]: event.target.value,
                            })
                          }
                        />
                      ) : (
                        <input
                          type={field.endsWith("_date") ? "date" : "text"}
                          value={draft[field]}
                          min={
                            field === "end_date"
                              ? draft.start_date || undefined
                              : undefined
                          }
                          onChange={(event) =>
                            setDraft({
                              ...draft,
                              [field]: event.target.value,
                            })
                          }
                          required={field !== "end_date"}
                        />
                      )}
                    </label>
                  ))}

                  <div className="medication-actions">
                    <button type="submit">Save changes</button>

                    <button
                      type="button"
                      className="cancel-button"
                      onClick={() => {
                        setEditingId(null);
                        setDraft(null);
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <div className="medication-icon"></div>

                  <h3>{medication.name}</h3>

                  <div className="medication-info">
                    <p>
                      <strong>Dose:</strong> {medication.dosage}
                    </p>

                    {medication.instructions && (
                      <p>
                        <strong>Instructions:</strong>{" "}
                        {medication.instructions}
                      </p>
                    )}

                    <p>
                      <strong>Start date:</strong> {medication.start_date}
                    </p>

                    {medication.end_date && (
                      <p>
                        <strong>End date:</strong> {medication.end_date}
                      </p>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={() => startEditing(medication)}
                  >
                    Edit
                  </button>
                </>
              )}
            </Box>
          ))}
        </div>
      )}
    </section>
  );
}

export default ViewMedications;