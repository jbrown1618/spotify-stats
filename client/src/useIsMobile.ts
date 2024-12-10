import { useCallback, useEffect, useState } from "react";

const mobileScreenSize = 768;
const mediaQuery = `(max-width: ${mobileScreenSize}px)`;

export function useIsMobile(): boolean {
  const [mobile, setMobile] = useState(window.matchMedia(mediaQuery).matches);

  const checkMobile = useCallback(
    (event: MediaQueryListEvent) => {
      if (mobile != event.matches) {
        setMobile(event.matches);
      }
    },
    [mobile]
  );

  useEffect(() => {
    const listener = window.matchMedia(mediaQuery);
    listener.addEventListener("change", checkMobile);
    return () => listener.removeEventListener("change", checkMobile);
  }, [checkMobile]);

  return mobile;
}
