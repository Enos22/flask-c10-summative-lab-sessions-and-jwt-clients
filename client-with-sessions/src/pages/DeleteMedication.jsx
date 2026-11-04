import { useEffect, useState } from "react";
import { apiRequest } from "../api";

function DeleteMedication() {
  const [medications, setMedications] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    let active = true;
    apiRequest("/api/medications/getmedications")
      .then((result) => { if (active) setMedications(result.medications || []); })
      .catch((error) => { if (active) setMessage(error.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  async function handleDelete(id) {
    if (!window.confirm("Delete this medication?")) return;
    setDeletingId(id);
    setMessage("");
    try {
      await apiRequest(`/api/medications/delete/${id}`, { method: "DELETE" });
      setMedications((current) => current.filter((item) => item.id !== id));
      setMessage("Medication deleted successfully.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section>
      <h2>Delete medication</h2>
      {loading ? <p>Loading medications…</p> : medications.length === 0 ? (
        <p>No medications found.</p>
      ) : medications.map((medication) => (
        <article key={medication.id}>
          <h3>{medication.name}</h3>
          <p>Dose: {medication.dosage}</p>
          <button type="button" disabled={deletingId === medication.id} onClick={() => handleDelete(medication.id)}>
            {deletingId === medication.id ? "Deleting…" : "Delete"}
          </button>
        </article>
      ))}
      {message && <p role="status">{message}</p>}
    </section>
  );
}

export default DeleteMedication;
