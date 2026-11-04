import { useState } from "react";
import { apiRequest } from "../api";

const emptyForm = {
  name: "",
  dosage: "",
  instructions: "",
  start_date: "",
  end_date: "",
};

function AddMedication() {
  const [formData, setFormData] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setIsSaving(true);

    try {
      await apiRequest("/api/medications/addmedication", {
        method: "POST",
        body: JSON.stringify({
          ...formData,
          instructions: formData.instructions || null,
          end_date: formData.end_date || null,
        }),
      });
      setMessage("Medication added successfully.");
      setFormData({ ...emptyForm });
    } catch (error) {
      setMessage(error.message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section>
      <h2>Add medication</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Name
          <input name="name" value={formData.name} onChange={handleChange} minLength={2} maxLength={100} required />
        </label>
        <label>
          Dose
          <input name="dosage" value={formData.dosage} onChange={handleChange} maxLength={100} required />
        </label>
        <label>
          Instructions
          <textarea name="instructions" value={formData.instructions} onChange={handleChange} />
        </label>
        <label>
          Start date
          <input type="date" name="start_date" value={formData.start_date} onChange={handleChange} required />
        </label>
        <label>
          End date (optional)
          <input type="date" name="end_date" value={formData.end_date} onChange={handleChange} min={formData.start_date || undefined} />
        </label>
        <button type="submit" disabled={isSaving}>
          {isSaving ? "Saving…" : "Add medication"}
        </button>
      </form>
      {message && <p role="status">{message}</p>}
    </section>
  );
}

export default AddMedication;
