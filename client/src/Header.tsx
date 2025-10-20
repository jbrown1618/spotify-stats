import { Filters } from "./Filters";
import styles from "./Header.module.css";

export function Header() {
  return (
    <nav className={styles.headerNav}>
      <h1 className={styles.headerText}>Spotify Stats</h1>
      <Filters />
    </nav>
  );
}
