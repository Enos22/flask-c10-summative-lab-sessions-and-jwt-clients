import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";
import { Button } from "../styles";
import { apiRequest } from "../api";

function TodayDoses() {
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingDose, setUpdatingDose] = useState(null);

  const loadDoses = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      // The daily report groups today's doses by status and ensures pending doses exist.
      const data = await apiRequest("/api/reports/daily");
      setReport(data);
    } catch (loadError) {
      setError(loadError.message || "Unable to load today’s doses.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDoses();
  }, [loadDoses]);

  async function updateDose(doseId, status) {
    setUpdatingDose(doseId);
    setError("");

    try {
      await apiRequest(`/api/doses/${doseId}/${status}`, {
        method: "PATCH",
        body: JSON.stringify({}),
      });
      // Reload the server's canonical dose/report state after each change.
      await loadDoses();
    } catch (updateError) {
      setError(updateError.message || "Unable to update dose.");
    } finally {
      setUpdatingDose(null);
    }
  }

  if (isLoading && !report) {
    return <Message>Loading today’s doses…</Message>;
  }

  if (error && !report) {
    return (
      <Panel>
        <Message role="alert">{error}</Message>
        <Button onClick={loadDoses}>Try again</Button>
      </Panel>
    );
  }

  const doses = report
    ? [...report.pending, ...report.taken, ...report.missed]
    : [];
  doses.sort((left, right) =>
    left.scheduled_time.localeCompare(right.scheduled_time)
  );

  return (
    <Panel>
      <Heading>Today’s doses</Heading>
      <Subheading>{report?.date}</Subheading>
      {error && <Message role="alert">{error}</Message>}
      {doses.length === 0 ? (
        <Message>No doses scheduled for today.</Message>
      ) : (
        <DoseList>
          {doses.map((dose) => (
            <DoseItem key={dose.dose_id}>
              <DoseInfo>
                <strong>{dose.medication_name}</strong>
                <span>{dose.dosage}</span>
                <span>
                  {new Date(dose.scheduled_time).toLocaleTimeString([], {
                    hour: "numeric",
                    minute: "2-digit",
                  })}
                </span>
                <Status status={dose.status}>{dose.status}</Status>
              </DoseInfo>
              {dose.recorded_status === "pending" && (
                <Actions>
                  <Button
                    disabled={updatingDose === dose.dose_id}
                    onClick={() => updateDose(dose.dose_id, "taken")}
                  >
                    {updatingDose === dose.dose_id ? "Saving…" : "Taken"}
                  </Button>
                  <Button
                    color="secondary"
                    disabled={updatingDose === dose.dose_id}
                    onClick={() => updateDose(dose.dose_id, "missed")}
                  >
                    Missed
                  </Button>
                </Actions>
              )}
            </DoseItem>
          ))}
        </DoseList>
      )}
      <Button variant="outline" onClick={loadDoses} disabled={isLoading}>
        {isLoading ? "Refreshing…" : "Refresh"}
      </Button>
    </Panel>
  );
}

const Panel = styled.section`
  max-width: 720px;
  margin: 32px auto;
  padding: 24px;
`;

const Heading = styled.h2`
  margin: 0;
`;

const Subheading = styled.p`
  color: #666;
`;

const DoseList = styled.ul`
  list-style: none;
  margin: 24px 0;
  padding: 0;
`;

const DoseItem = styled.li`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #e5e5e5;

  @media (max-width: 560px) {
    align-items: flex-start;
    flex-direction: column;
  }
`;

const DoseInfo = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
`;

const Status = styled.span`
  text-transform: capitalize;
  font-weight: 600;
  color: ${({ status }) =>
    status === "taken" ? "seagreen" : status === "missed" ? "firebrick" : "darkorange"};
`;

const Actions = styled.div`
  display: flex;
  gap: 8px;
`;

const Message = styled.p`
  margin: 16px 0;
`;

export default TodayDoses;
