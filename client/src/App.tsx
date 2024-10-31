import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

(async function () {
  const artists = [
    "spotify:artist:6YVMFz59CuY7ngCxTxjpxE",
    "spotify:artist:5t5FqBwTcgKTaWmfEbwQY9",
  ];

  const query = new URLSearchParams();
  query.append("artists", encodeURIComponent(JSON.stringify(artists)));

  const res = await fetch("/api/data?" + query.toString());
  if (!res.ok) return;

  console.log(await res.json());
})();

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
