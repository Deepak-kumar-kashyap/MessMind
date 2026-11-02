const API = "http://127.0.0.1:8000";
const $ = (id) => document.getElementById(id);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
async function request(path, options={}) {
  const response = await fetch(`${API}${path}`, {headers:{"Content-Type":"application/json",...(options.headers||{})},...options});
  const data = await response.json().catch(()=>({detail:"Unexpected server response"}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}
async function loadHealth() {
  const el = $("dbStatus");
  try {
    const data = await request("/api/health");
    el.classList.toggle("offline", !data.mongodb.connected);
    el.innerHTML = `<i></i><span>${data.mongodb.connected ? "MongoDB connected" : "MongoDB not connected"}</span>`;
    el.title = data.mongodb.message;
  } catch (error) {
    el.classList.add("offline"); el.innerHTML = "<i></i><span>API not running</span>"; el.title = error.message;
  }
}
async function loadMetrics() {
  try {
    const m = await request("/api/metrics");
    $("trainPercent").textContent = `${m.train_percent}%`;
    $("testPercent").textContent = `${m.test_percent}%`;
    $("mae").textContent = `${m.mae} plates`;
    $("rmse").textContent = `${m.rmse} plates`;
    $("r2").textContent = m.r2;
    $("testRows").textContent = Number(m.testing_rows).toLocaleString();
    $("evaluationNote").textContent = `Trained on ${m.training_rows.toLocaleString()} rows and tested on ${m.testing_rows.toLocaleString()} separate rows. Baseline MAE: ${m.baseline_mae} plates.`;
  } catch (error) { $("evaluationNote").textContent = `Model metrics unavailable: ${error.message}`; }
}
async function loadHistory() {
  const body = $("historyBody");
  try {
    const rows = await request("/api/history?limit=8");
    if (!rows.length) { body.innerHTML = '<tr><td colspan="4" class="empty">No predictions saved yet. Make your first forecast above.</td></tr>'; return; }
    body.innerHTML = rows.filter(r => r.record_type === "prediction").map(r => `<tr><td>${esc(r.item)}</td><td>${esc(r.day)} · ${esc(r.meal)}</td><td><b>${esc(r.predicted_demand)}</b></td><td>${r.created_at ? new Date(r.created_at).toLocaleString() : "—"}</td></tr>`).join("") || '<tr><td colspan="4" class="empty">No predictions saved yet.</td></tr>';
  } catch (error) { body.innerHTML = `<tr><td colspan="4" class="empty">${esc(error.message)}. Check your MongoDB connection.</td></tr>`; }
}
async function refresh() { await Promise.all([loadHealth(), loadHistory()]); }
function showResult(html) { const el = $("predictResult"); el.innerHTML = html; el.classList.remove("hidden"); }
$("predictForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = $("predictBtn"); button.disabled = true; button.textContent = "Predicting…";
  const payload = {day:$("day").value, meal:$("meal").value, item:$("item").value, weather:$("weather").value, event:$("event").value};
  try {
    const result = await request("/api/predict", {method:"POST", body:JSON.stringify(payload)});
    showResult(`<span class="result-label">Estimated demand</span><strong>${esc(result.predicted_demand)} plates</strong><p>${esc(payload.item)} for ${esc(payload.meal)} on ${esc(payload.day)}.</p><small>${esc(result.mongodb_message)}</small>`);
    await refresh();
  } catch (error) { showResult(`<p class="error">Prediction failed: ${esc(error.message)}</p>`); }
  finally { button.disabled = false; button.innerHTML = 'Predict required plates <span>→</span>'; }
});
$("refreshBtn").addEventListener("click", refresh);
loadMetrics(); refresh();
