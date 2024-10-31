(async function () {
  const artists = [
    "spotify:artist:6YVMFz59CuY7ngCxTxjpxE",
    "spotify:artist:5t5FqBwTcgKTaWmfEbwQY9",
  ];

  const query = new URLSearchParams();
  query.append("artists", encodeURIComponent(JSON.stringify(artists)));

  const res = await fetch("/data?" + query.toString());
  if (!res.ok) return;

  console.log(await res.json());
})();
