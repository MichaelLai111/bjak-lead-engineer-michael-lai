const questionForm = document.querySelector('#question-form');
const questionInput = document.querySelector('#question');
const questionCount = document.querySelector('#question-count');
const answerTitle = document.querySelector('#answer-title');
const answerStatus = document.querySelector('#answer-status');
const answerContent = document.querySelector('#answer-content');
const responseMeta = document.querySelector('#response-meta');
const sourceCount = document.querySelector('#source-count');
const sourcesList = document.querySelector('#sources-list');
const metricsGrid = document.querySelector('#metrics-grid');
const categoryList = document.querySelector('#category-list');
const failureList = document.querySelector('#failure-list');
const failureCount = document.querySelector('#failure-count');
const submitButton = questionForm.querySelector('button[type="submit"]');

const metricDefinitions = [
  ['case_pass_rate_percent', 'Case pass rate', '%'],
  ['groundedness_percent', 'Groundedness', '%'],
  ['citation_accuracy_percent', 'Citation accuracy', '%'],
  ['adversarial_safety_percent', 'Adversarial safety', '%'],
];

questionInput.addEventListener('input', () => {
  questionCount.textContent = `${questionInput.value.length.toLocaleString()} / 2,000`;
});

document.querySelectorAll('.prompt-chip').forEach((button) => {
  button.addEventListener('click', () => {
    questionInput.value = button.dataset.question;
    questionInput.dispatchEvent(new Event('input'));
    questionInput.focus();
  });
});

questionInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    questionForm.requestSubmit();
  }
});

questionForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;
  setLoading(true);
  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'Request failed');
    renderResponse(payload);
  } catch (error) {
    renderError(error.message);
  } finally {
    setLoading(false);
  }
});

function setLoading(loading) {
  submitButton.disabled = loading;
  submitButton.querySelector('span:first-child').textContent = loading ? 'Checking evidence…' : 'Ask assistant';
  answerTitle.textContent = loading ? 'Following the evidence…' : answerTitle.textContent;
  if (loading) answerStatus.className = 'status-badge status-idle';
}

function renderResponse(response) {
  answerTitle.textContent = response.status === 'answered' ? 'Here is what the record says' : 'The record stops here';
  answerStatus.textContent = response.status.replace('_', ' ');
  answerStatus.className = `status-badge status-${response.status}`;
  answerContent.className = 'answer-content';
  answerContent.textContent = response.answer;
  responseMeta.className = 'response-meta';
  responseMeta.innerHTML = `<span>${response.sources.length} source${response.sources.length === 1 ? '' : 's'}</span><span>${response.latency_ms.toFixed(3)} ms</span>${response.reason ? `<span>${escapeHtml(response.reason)}</span>` : ''}`;
  sourceCount.textContent = `${response.sources.length} source${response.sources.length === 1 ? '' : 's'}`;
  if (!response.sources.length) {
    sourcesList.className = 'sources-list empty-sources';
    sourcesList.innerHTML = '<div class="source-placeholder"><span>∅</span><p>No evidence met the threshold. The assistant did not invent a claim.</p></div>';
    return;
  }
  sourcesList.className = 'sources-list';
  sourcesList.innerHTML = response.sources.map((source) => `
    <article class="source-item">
      <div class="source-item-top"><span class="source-section">${escapeHtml(source.section)}</span><span class="source-score">score ${source.score.toFixed(2)}</span></div>
      <div class="source-title">${escapeHtml(source.title)}</div>
      <div class="source-id">${escapeHtml(source.chunk_id)}</div>
    </article>
  `).join('');
}

function renderError(message) {
  answerTitle.textContent = 'The local service returned an error';
  answerStatus.textContent = 'error';
  answerStatus.className = 'status-badge status-refused';
  answerContent.className = 'answer-content';
  answerContent.textContent = message;
  responseMeta.className = 'response-meta hidden';
}

async function loadSummary() {
  try {
    const response = await fetch('/api/summary');
    const summary = await response.json();
    if (!summary.available) throw new Error(summary.reason);
    renderMetrics(summary);
  } catch (error) {
    metricsGrid.innerHTML = `<div class="metric-card error-card">Evaluation unavailable<br /><small>${escapeHtml(error.message)}</small></div>`;
  }
}

function renderMetrics(summary) {
  const metrics = summary.metrics || {};
  metricsGrid.innerHTML = metricDefinitions.map(([key, label, suffix]) => `
    <div class="metric-card">
      <span class="metric-label">${label}</span>
      <strong class="metric-value">${metrics[key] ?? '—'}${suffix}</strong>
      <span class="metric-caption">${key === 'case_pass_rate_percent' ? `${summary.case_count} committed cases` : 'measured result'}</span>
    </div>
  `).join('');

  const categories = summary.categories || {};
  categoryList.innerHTML = Object.entries(categories).map(([name, details]) => `
    <div class="category-row"><span class="category-name">${formatCategory(name)}</span><span class="category-bar"><span class="category-fill" style="width:${details.pass_rate_percent}%"></span></span><span class="category-rate">${details.pass_rate_percent}%</span></div>
  `).join('');

  const failures = summary.failed_case_ids || [];
  failureCount.textContent = `${failures.length} cases`;
  failureList.innerHTML = failures.length ? failures.map((failure) => `<span class="failure-tag">${escapeHtml(failure)}</span>`).join('') : '<span class="failure-tag">No known failures</span>';
}

function formatCategory(value) {
  return value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
}

loadSummary();
