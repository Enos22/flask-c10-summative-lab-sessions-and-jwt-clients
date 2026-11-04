import styled from "styled-components";

const Box = styled.div`
  background: #535454;
  border: 1px solid #c5dfd2;
  border-radius: 18px;
  box-shadow: 0 8px 25px rgba(23, 51, 42, 0.08);
  padding: 25px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(23, 51, 42, 0.13);
  }
`;

export default Box;