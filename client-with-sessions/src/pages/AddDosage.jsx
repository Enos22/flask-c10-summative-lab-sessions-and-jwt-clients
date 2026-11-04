import { useEffect, useState } from "react";
import { apiRequest } from "../api";

const weekDays = [
  ["mon", "Monday"], ["tue", "Tuesday"], ["wed", "Wednesday"],
  ["thu", "Thursday"], ["fri", "Friday"], ["sat", "Saturday"], ["sun", "Sunday"],
];

function AddDosage() {
  const [medications, setMedications] = useState([]);
  const [formData, setFormData] = useState({
    medication_id: "",
    reminder_time: "",
    days_of_week: [],
    is_active: true,
  });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let active = true;
    apiRequest("/api/medications/getmedications")
      .then((result) => { if (active) setMedications(result.medications || []); })
      .catch((error) => { if (active) setMessage(error.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  function toggleDay(day) {
    setFormData((current) => ({
      ...current,
      days_of_week: current.days_of_week.includes(day)
        ? current.days_of_week.filter((item) => item !== day)
        : [...current.days_of_week, day],
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setIsSaving(true);
    try {
      await apiRequest("/api/schedules", {
        method: "POST",
        body: JSON.stringify({
          ...formData,
          medication_id: Number(formData.medication_id),
        }),
      });
      setMessage("Schedule added successfully.");
      setFormData({ medication_id: "", reminder_time: "", days_of_week: [], is_active: true });
    } catch (error) {
      setMessage(error.message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section>
      <h2>Add medication schedule</h2>
      {loading ? <p>Loading medications…</p> : medications.length === 0 ? (
        <p>Add a medication before creating its schedule.</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <label>
            Medication
            <select
              name="medication_id"
              value={formData.medication_id}
              onChange={(event) => setFormData({ ...formData, medication_id: event.target.value })}
              required
            >
              <option value="">Choose medication</option>
              {medications.map((medication) => (
                <option key={medication.id} value={medication.id}>
                  {medication.name} — {medication.dosage}
                </option>
              ))}
            </select>
          </label>
          <label>
            Reminder time
            <input
              type="time"
              value={formData.reminder_time}
              onChange={(event) => setFormData({ ...formData, reminder_time: event.target.value })}
              required
            />
          </label>
          <fieldset>
            <legend>Days of the week</legend>
            {weekDays.map(([value, label]) => (
              <label key={value}>
                <input type="checkbox" checked={formData.days_of_week.includes(value)} onChange={() => toggleDay(value)} />
                {label}
              </label>
            ))}
          </fieldset>
          <button type="submit" disabled={isSaving || formData.days_of_week.length === 0}>
            {isSaving ? "Saving…" : "Add schedule"}
          </button>
        </form>
      )}
      {message && <p role="status">{message}</p>}
    </section>
  );
}

export default AddDosage;
