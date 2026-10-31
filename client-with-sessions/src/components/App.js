import React, { useEffect, useState } from "react";
import NavBar from "./NavBar";
import Login from "../pages/Login";

function App() {
  const [user, setUser] = useState(null);

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
      <NavBar user={user} setUser={setUser} />
      <main>
        <p>You are logged in!</p>
      </main>
    </>
  );
}

export default App;
