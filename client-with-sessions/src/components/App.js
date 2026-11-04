import React, { useEffect, useState } from "react";
import { Switch, Route, Redirect } from "react-router-dom";
import ViewMedications from "../pages/ViewMedications";
import ViewDoses from "../pages/ViewDoses";
import NavBar from "./NavBar";
import Login from "../pages/Login";
import TodayDoses from "../pages/TodayDoses";

import AddMedication from "../pages/AddMedication";
import DeleteMedication from "../pages/DeleteMedication";
import AddDosage from "../pages/AddDosage";
import DeleteDosage from "../pages/DeleteDosage";
import { apiRequest } from "../api";
import "./app.css";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRequest("/check_session")
      .then(setUser)
      .catch((error) => {
        // An unauthenticated session is expected on a fresh visit.
        if (!/authentication required/i.test(error.message)) {
          console.error("Could not check the login session:", error);
        }
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Checking session...</p>;

  if (!user) return <Login onLogin={setUser} />;

  return (
    <>
      <NavBar setUser={setUser} />

      <main>
        <Switch>
          <Route exact path="/" render={() => <h2>You are logged in!</h2>} />

          <Route
              exact
              path="/view-medications"
              component={ViewMedications}
          />

          <Route
                exact
                path="/view-doses"
                component={ViewDoses}
            /> 
          <Route exact path="/today-doses" component={TodayDoses} />

          <Route exact path="/add-medication" component={AddMedication} />

          <Route exact path="/delete-medication" component={DeleteMedication} />

          <Route exact path="/add-dosage" component={AddDosage} />

          <Route exact path="/delete-dosage" component={DeleteDosage} />

          <Redirect to="/" />
        </Switch>
      </main>
    </>
  );
}

export default App;
