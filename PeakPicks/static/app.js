async function postPick(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  const res = await fetch("/api/picks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  return res.json().then(j => ({ ok: res.ok, body: j }));
}

async function loadPicks(category = "") {
  const url = category ? `/api/picks?category=${encodeURIComponent(category)}` : "/api/picks";
  const res = await fetch(url);
  return res.json();
}

function renderPick(p) {
  const tags = (p.tags || []).map(t => `#${t}`).join(" ");
  return `
    <div class="pick">
      <div class="rank">${p.rank}</div>
      <div><b>${p.name}</b></div>
      <div class="small">${p.category}</div>
      ${p.reason ? `<p>${p.reason}</p>` : ""}
      ${tags ? `<div class="small">${tags}</div>` : ""}
      ${p.image_url ? `<img src="${p.image_url}" alt="image" />` : ""}
    </div>
  `;
}

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("pickForm");
  const msg = document.getElementById("msg");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.textContent = "Saving...";
      const { ok, body } = await postPick(form);
      if (!ok) {
        msg.textContent = body.error || "Failed to save.";
        return;
      }
      msg.textContent = "Saved! Add another or go view picks.";
      form.reset();
    });
  }

  const list = document.getElementById("list");
  const filterForm = document.getElementById("filterForm");

  async function refresh(category) {
    if (!list) return;
    list.innerHTML = "Loading...";
    const picks = await loadPicks(category);
    if (!picks.length) {
      list.innerHTML = "<div class='card'>No picks yet. Create one!</div>";
      return;
    }
    list.innerHTML = picks.map(renderPick).join("");
  }

  if (list) {
    const input = document.getElementById("category");
    const cat = (typeof initialCategory === "string" && initialCategory) ? initialCategory : "";
    if (input) input.value = cat;
    await refresh(cat);

    if (filterForm) {
      filterForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        await refresh((input?.value || "").trim());
      });
    }
  }
});
