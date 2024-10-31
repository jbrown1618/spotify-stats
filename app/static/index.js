(async function () {
  const res = await fetch("/tracks");
  if (!res.ok) return;

  console.log(await res.text());
})();
