import React, { useEffect, useState } from "react";
import NavBar from "./NavBar";
import Login from "../pages/Login";
import TodayDoses from "../pages/TodayDoses";

function App() {
  const [user, setUser] = useState(null);
  // Keep the dose view opt-in so the existing post-login screen stays the default.
  const [showDoses, setShowDoses] = useState(false);

  useEffect(() => {
    fetch("/check_session").then((r) => {
      if (r.ok) {
        r.json().then((user) => setUser(user));
      }
    });
  }, []);

  if (!user) return <Login onLogin={setUser} />;

  return (
    <>
    
      <NavBar
        user={user}
        setUser={setUser}
        onShowDoses={() => setShowDoses(true)}
      />
      <main>
        {showDoses ? <TodayDoses /> : <p>You are logged in!</p>}
      </main>
    </>
  );
}

export default App;
