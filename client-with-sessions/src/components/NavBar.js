import React from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { Button } from "../styles";
import { apiRequest } from "../api";

function NavBar({ setUser }) {

  async function handleLogoutClick() {
    try {
      await apiRequest("/logout", { method: "DELETE" });
      setUser(null);
    } catch (error) {
      window.alert(error.message);
    }
  }

  return (
    <Wrapper>
      <Logo>
        <Link to="/">My App</Link>
      </Logo>

      <Nav>

        <Button as={Link} to="/view-medications">
    View Medications
</Button>

<Button as={Link} to="/view-doses">
    View Doses
</Button> 
        <Button as={Link} to="/today-doses">
          Today's doses
        </Button>

        <Button as={Link} to="/add-medication">
          Add medication
        </Button>

        <Button as={Link} to="/delete-medication">
          Delete medication
        </Button>

        <Button as={Link} to="/add-dosage">
          Add schedule
        </Button>

        <Button as={Link} to="/delete-dosage">
          Manage schedules
        </Button>

        <Button variant="outline" onClick={handleLogoutClick}>
          Logout
        </Button>
      </Nav>
    </Wrapper>
  );
}

const Wrapper = styled.header`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
`;

const Logo = styled.h1`
  font-family: "Permanent Marker", cursive;
  font-size: 3rem;
  color: deeppink;
  margin: 0;
  line-height: 1;

  a {
    color: inherit;
    text-decoration: none;
  }
`;

const Nav = styled.nav`
  display: flex;
  gap: 4px;
  position: absolute;
  right: 8px;
`;

export default NavBar;
