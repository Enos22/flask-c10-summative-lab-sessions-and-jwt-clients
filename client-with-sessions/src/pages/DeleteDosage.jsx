import { useEffect, useState } from "react";
import { apiRequest } from "../api";

const weekDays = [
  ["mon", "Monday"], ["tue", "Tuesday"], ["wed", "Wednesday"],
  ["thu", "Thursday"], ["fri", "Friday"], ["sat", "Saturday"], ["sun", "Sunday"],
];

function DeleteDosage() {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [draft, setDraft] = useState(null);
  const [busyId, setBusyId] = useState(null);

  useEffect(() => {
    let active = true;
    apiRequest("/api/schedules?per_page=50")
      .then((result) => { if (active) setSchedules(result.items || []); })
      .catch((error) => { if (active) setMessage(error.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  function beginEdit(schedule) {
    setEditingId(schedule.id);
    setDraft({
      reminder_time: schedule.reminder_time,
      days_of_week: schedule.days_of_week || [],
      is_active: schedule.is_active,
    });
  }

  function toggleDay(day) {
    setDraft((current) => ({
      ...current,
      days_of_week: current.days_of_week.includes(day)
        ? current.days_of_week.filter((item) => item !== day)
        : [...current.days_of_week, day],
    }));
  }

  async function saveSchedule(event) {
    event.preventDefault();
    setMessage("");
    setBusyId(editingId);
    try {
      const updated = await apiRequest(`/api/schedules/${editingId}`, {
        method: "PATCH",
        body: JSON.stringify(draft),
      });
      setSchedules((current) => current.map((item) => item.id === editingId ? updated : item));
      setEditingId(null);
      setDraft(null);
      setMessage("Schedule updated successfully.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusyId(null);
    }
  }

  async function handleDelete(scheduleId) {
    if (!window.confirm("Delete this medication schedule?")) return;
    setMessage("");
    setBusyId(scheduleId);
    try {
      await apiRequest(`/api/schedules/${scheduleId}`, { method: "DELETE" });
      setSchedules((current) => current.filter((item) => item.id !== scheduleId));
      setMessage("Schedule deleted successfully.");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section>
      <h2>Manage medication schedules</h2>
      {loading ? <p>Loading schedules…</p> : schedules.length === 0 ? (
        !message && <p>No schedules found.</p>
      ) : schedules.map((schedule) => (
        <article key={schedule.id}>
          <h3>Schedule #{schedule.id} · Medication #{schedule.medication_id}</h3>
          {editingId === schedule.id ? (
            <form onSubmit={saveSchedule}>
              <label>
                Reminder time
                <input type="time" value={draft.reminder_time} onChange={(event) => setDraft({ ...draft, reminder_time: event.target.value })} required />
              </label>
              <fieldset>
                <legend>Days of the week</legend>
                {weekDays.map(([value, label]) => (
                  <label key={value}>
                    <input type="checkbox" checked={draft.days_of_week.includes(value)} onChange={() => toggleDay(value)} />
                    {label}
                  </label>
                ))}
              </fieldset>
              <label>
                <input type="checkbox" checked={draft.is_active} onChange={(event) => setDraft({ ...draft, is_active: event.target.checked })} />
                Active
              </label>
              <button type="submit" disabled={busyId === schedule.id || draft.days_of_week.length === 0}>Save changes</button>
              <button type="button" onClick={() => { setEditingId(null); setDraft(null); }}>Cancel</button>
            </form>
          ) : (
            <>
              <p>Reminder: {schedule.reminder_time}</p>
              <p>Days: {(schedule.days_of_week || []).join(", ")}</p>
              <p>Status: {schedule.is_active ? "Active" : "Inactive"}</p>
              <button type="button" onClick={() => beginEdit(schedule)}>Edit</button>
              <button type="button" disabled={busyId === schedule.id} onClick={() => handleDelete(schedule.id)}>
                {busyId === schedule.id ? "Deleting…" : "Delete"}
              </button>
            </>
          )}
        </article>
      ))}
      {message && <p role="status">{message}</p>}
    </section>
  );
}

export default DeleteDosage;
