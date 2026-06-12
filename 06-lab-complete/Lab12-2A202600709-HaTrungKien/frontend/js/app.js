const MAX_SELECTED_SEEDS = 2;
const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const LOADING_STEPS = [
  "Analyzing your vibe...",
  "Processing aesthetic patterns...",
  "Running similarity embeddings...",
  "Finding your perfect match...",
  "Almost there...",
];

const state = {
  seedDeck: [],
  deckIndex: 0,
  selectedSeedCafes: [],
  excludedSeedCafeIds: new Set(),
  excludedResultCafeIds: new Set(),
  hasMoreSeedOptions: true,
  recommendation: null,
  topResults: [],
  currentDetailCafe: null,
  isLoadingSeeds: false,
  isAnalyzing: false,
  loadingIntervalId: null,
};

const elements = {
  clock: document.getElementById("clock"),
  deck: document.getElementById("deck"),
  deckEmpty: document.getElementById("deck-empty"),
  loadingText: document.getElementById("loading-txt"),
  loadingBar: document.getElementById("loading-bar"),
  resultsDesc: document.getElementById("results-desc"),
  resultsTags: document.getElementById("results-tags"),
  resultsList: document.getElementById("results-list"),
  toasts: document.getElementById("toasts"),
  likeLabel: document.getElementById("like-label"),
  likeDots: [
    document.getElementById("dot-1"),
    document.getElementById("dot-2"),
    document.getElementById("dot-3"),
  ],
  buttons: {
    nope: document.getElementById("btn-nope"),
    like: document.getElementById("btn-love"),
    location: document.getElementById("btn-location"),
  },
  detail: {
    image: document.getElementById("d-img"),
    match: document.getElementById("d-match"),
    name: document.getElementById("d-name"),
    cat: document.getElementById("d-cat"),
    address: document.getElementById("d-address"),
    rating: document.getElementById("d-rating"),
    category: document.getElementById("d-category"),
    reason: document.getElementById("d-reason"),
    mapsButton: document.getElementById("d-maps-btn"),
    spectrum: document.getElementById("d-spectrum"),
    busy: document.getElementById("d-busy"),
  },
};

const api = {
  async listSeedCafes(excludedSeedCafeIds) {
    const params = new URLSearchParams();
    excludedSeedCafeIds.forEach((id) => {
      params.append("excluded_seed_cafe_ids", id);
    });
    const query = params.toString();
    return requestJson(`/api/seed-cafes${query ? `?${query}` : ""}`);
  },

  async recommend(selectedSeedCafeIds, excludedResultCafeIds) {
    return requestJson("/api/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        selected_seed_cafe_ids: selectedSeedCafeIds,
        excluded_result_cafe_ids: excludedResultCafeIds,
      }),
    });
  },
};

function getApiBaseUrl() {
  const configuredBaseUrl =
    window.COFFEEHOLIC_CONFIG?.apiBaseUrl || document.body.dataset.apiBaseUrl;
  if (configuredBaseUrl) {
    return configuredBaseUrl.replace(/\/$/, "");
  }

  if (window.location.protocol === "file:") {
    return DEFAULT_API_BASE_URL;
  }

  if (
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "localhost"
  ) {
    if (window.location.port === "8000") {
      return window.location.origin;
    }
    return DEFAULT_API_BASE_URL;
  }

  return window.location.origin;
}

async function requestJson(path, options = {}) {
  const { allowNoContent = false, ...fetchOptions } = options;
  const response = await fetch(`${getApiBaseUrl()}${path}`, fetchOptions);

  if (!response.ok) {
    throw new Error(await buildApiErrorMessage(response));
  }

  if (allowNoContent || response.status === 204) {
    return null;
  }

  return response.json();
}

async function buildApiErrorMessage(response) {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string") {
      return payload.detail;
    }
  } catch (_error) {
    // Ignore JSON parsing errors and fall through to status text.
  }

  return `Request failed: ${response.status} ${response.statusText}`;
}

function updateClock() {
  const now = new Date();
  let hours = now.getHours();
  const minutes = now.getMinutes();
  const period = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;
  elements.clock.textContent = `${hours}:${String(minutes).padStart(2, "0")} ${period}`;
}

function showScreen(screenId) {
  document.querySelectorAll(".screen").forEach((screen) => {
    screen.classList.add("hidden");
  });
  document.getElementById(screenId).classList.remove("hidden");
}

function goBack(targetScreenId) {
  showScreen(targetScreenId);
}

function openExternalUrl(url) {
  if (!url) {
    toast("This cafe does not have a Google Maps link yet.", "warn");
    return;
  }
  window.open(url, "_blank", "noopener,noreferrer");
}

function wait(milliseconds) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function renderStars(rating, size = 13) {
  const fullStars = Math.floor(rating);
  let starsMarkup = "";
  for (let index = 0; index < 5; index += 1) {
    const fill = index < fullStars ? "currentColor" : "none";
    starsMarkup += `
      <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="${fill}" stroke="#C4956A" stroke-width="2">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
    `;
  }
  return starsMarkup;
}

function roundMatchPercentage(score) {
  return Math.round(score * 100);
}

function resetLoadingAnimation() {
  if (state.loadingIntervalId) {
    window.clearInterval(state.loadingIntervalId);
    state.loadingIntervalId = null;
  }
  elements.loadingText.textContent = LOADING_STEPS[0];
  elements.loadingBar.style.animation = "none";
  void elements.loadingBar.offsetWidth;
  elements.loadingBar.style.animation = "loading-bar 3s ease-out forwards";
}

function disableSwipeButtons(disabled) {
  Object.values(elements.buttons).forEach((button) => {
    button.disabled = disabled;
    button.style.opacity = disabled ? "0.55" : "";
    button.style.cursor = disabled ? "not-allowed" : "";
  });
}

function setDeckEmptyState(message) {
  elements.deckEmpty.querySelector("p").innerHTML = message;
  elements.deckEmpty.style.display = "flex";
}

function hideDeckEmptyState() {
  elements.deckEmpty.style.display = "none";
}

function updateSelectionCounter() {
  elements.likeDots.forEach((dot, index) => {
    if (!dot) {
      return;
    }

    if (index >= MAX_SELECTED_SEEDS) {
      dot.style.display = "none";
      return;
    }

    dot.style.display = "";
    dot.classList.toggle("filled", index < state.selectedSeedCafes.length);
  });

  elements.likeLabel.textContent = `${state.selectedSeedCafes.length}/${MAX_SELECTED_SEEDS}`;
}

function resetSwipeSession() {
  state.seedDeck = [];
  state.deckIndex = 0;
  state.selectedSeedCafes = [];
  state.excludedSeedCafeIds = new Set();
  state.excludedResultCafeIds = new Set();
  state.hasMoreSeedOptions = true;
  state.recommendation = null;
  state.topResults = [];
  state.currentDetailCafe = null;
  state.isLoadingSeeds = false;
  state.isAnalyzing = false;
  updateSelectionCounter();
}

async function goToSwipe() {
  resetSwipeSession();
  showScreen("screen-swipe");
  await loadSeedDeck();
}

async function loadSeedDeck() {
  if (state.isLoadingSeeds) {
    return;
  }

  state.isLoadingSeeds = true;
  disableSwipeButtons(true);
  hideDeckEmptyState();

  try {
    const payload = await api.listSeedCafes([...state.excludedSeedCafeIds]);
    state.seedDeck = payload.seed_cafes;
    state.deckIndex = 0;
    state.hasMoreSeedOptions = payload.has_more;

    if (payload.fallback_message) {
      toast(payload.fallback_message, "warn");
    }

    renderDeck();
  } catch (error) {
    state.seedDeck = [];
    state.deckIndex = 0;
    setDeckEmptyState("We could not load cafe options right now.<br>Please try again.");
    toast(error.message, "warn");
  } finally {
    state.isLoadingSeeds = false;
    disableSwipeButtons(false);
  }
}

function getCurrentSeedCafe() {
  return state.seedDeck[state.deckIndex] || null;
}

function renderDeck() {
  elements.deck.querySelectorAll(".cafe-card").forEach((card) => card.remove());

  const remainingCafes = state.seedDeck.slice(state.deckIndex);
  if (!remainingCafes.length) {
    void handleDeckExhausted();
    return;
  }

  hideDeckEmptyState();
  const cafesToRender = remainingCafes.slice(0, 3).reverse();
  cafesToRender.forEach((cafe, index) => {
    const isTopCard = index === cafesToRender.length - 1;
    const stackIndex = cafesToRender.length - 1 - index;
    const card = buildSeedCard(cafe, isTopCard, stackIndex);
    elements.deck.appendChild(card);
  });

  const topCard = elements.deck.querySelector(".top-card");
  const currentCafe = getCurrentSeedCafe();
  if (topCard && currentCafe) {
    attachSwipe(topCard, currentCafe);
  }
}

async function handleDeckExhausted() {
  if (state.selectedSeedCafes.length > 0) {
    await startAnalysis();
    return;
  }

  if (state.hasMoreSeedOptions) {
    toast("Refreshing cafe options...", "info");
    await loadSeedDeck();
    return;
  }

  setDeckEmptyState("You've seen all available seed cafes.<br>Please refresh and try again.");
}

function buildSeedCard(cafe, isTopCard, stackIndex) {
  const card = document.createElement("div");
  const stackClass = isTopCard
    ? "top-card"
    : stackIndex === 1
      ? "bg-card-1"
      : "bg-card-2";
  card.className = `cafe-card ${stackClass}`;
  card.dataset.id = cafe.id;

  card.innerHTML = `
    <div class="card-info-top">
      <div class="card-cafe-name"></div>
      <div class="card-stars"><span class="star-icons"></span><span class="star-value"></span></div>
      <div class="card-address">
        <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        <span class="address-value"></span>
      </div>
    </div>
    <img class="card-photo" loading="lazy" draggable="false">
    <div class="stamp stamp-like">LIKE</div>
    <div class="stamp stamp-nope">NOPE</div>
  `;

  card.querySelector(".card-cafe-name").textContent = cafe.name;
  card.querySelector(".star-icons").innerHTML = renderStars(cafe.rating);
  card.querySelector(".star-value").textContent = cafe.rating;
  card.querySelector(".address-value").textContent = cafe.address;

  const image = card.querySelector(".card-photo");
  image.src = cafe.image_url;
  image.alt = cafe.name;

  return card;
}

function attachSwipe(cardElement, cafe) {
  let startX = 0;
  let startY = 0;
  let dragging = false;

  const handleStart = (event) => {
    dragging = true;
    const point = event.touches ? event.touches[0] : event;
    startX = point.clientX;
    startY = point.clientY;
    cardElement.style.transition = "none";

    document.addEventListener("mousemove", handleMove);
    document.addEventListener("touchmove", handleMove, { passive: false });
    document.addEventListener("mouseup", handleEnd);
    document.addEventListener("touchend", handleEnd);
  };

  const handleMove = (event) => {
    if (!dragging) {
      return;
    }

    if (event.cancelable) {
      event.preventDefault();
    }

    const point = event.touches ? event.touches[0] : event;
    const deltaX = point.clientX - startX;
    const deltaY = point.clientY - startY;
    const rotation = deltaX * 0.07;

    cardElement.style.transform = `translate(${deltaX}px, ${deltaY}px) rotate(${rotation}deg)`;

    const likeStamp = cardElement.querySelector(".stamp-like");
    const nopeStamp = cardElement.querySelector(".stamp-nope");

    if (deltaX > 20) {
      likeStamp.style.opacity = String(Math.min((deltaX - 20) / 80, 1));
      nopeStamp.style.opacity = "0";
      return;
    }

    if (deltaX < -20) {
      nopeStamp.style.opacity = String(Math.min((-deltaX - 20) / 80, 1));
      likeStamp.style.opacity = "0";
      return;
    }

    likeStamp.style.opacity = "0";
    nopeStamp.style.opacity = "0";
  };

  const handleEnd = (event) => {
    if (!dragging) {
      return;
    }

    dragging = false;
    document.removeEventListener("mousemove", handleMove);
    document.removeEventListener("touchmove", handleMove);
    document.removeEventListener("mouseup", handleEnd);
    document.removeEventListener("touchend", handleEnd);

    const point = event.changedTouches ? event.changedTouches[0] : event;
    const deltaX = point.clientX - startX;

    cardElement.style.transition =
      "transform .35s cubic-bezier(.25,.8,.25,1), opacity .25s";

    if (deltaX > 100) {
      doLike(cardElement, cafe);
      return;
    }

    if (deltaX < -100) {
      doNope(cardElement, cafe);
      return;
    }

    cardElement.style.transform = "";
    cardElement.querySelectorAll(".stamp").forEach((stamp) => {
      stamp.style.opacity = "0";
    });
  };

  cardElement.addEventListener("mousedown", handleStart);
  cardElement.addEventListener("touchstart", handleStart, { passive: true });
}

function doLike(cardElement, cafe) {
  if (state.selectedSeedCafes.length >= MAX_SELECTED_SEEDS) {
    return;
  }

  cardElement.style.transform = "translate(600px,-50px) rotate(25deg)";
  cardElement.style.opacity = "0";

  state.selectedSeedCafes.push(cafe);
  state.excludedSeedCafeIds.add(cafe.id);
  state.deckIndex += 1;
  updateSelectionCounter();

  if (state.selectedSeedCafes.length === 1) {
    toast("Pick one more cafe, or skip the rest to continue.", "info");
  }

  window.setTimeout(() => {
    cardElement.remove();
    if (state.selectedSeedCafes.length >= MAX_SELECTED_SEEDS) {
      void startAnalysis();
      return;
    }
    renderDeck();
  }, 320);
}

function doNope(cardElement, cafe) {
  cardElement.style.transform = "translate(-600px,-50px) rotate(-25deg)";
  cardElement.style.opacity = "0";
  state.excludedSeedCafeIds.add(cafe.id);
  state.deckIndex += 1;

  window.setTimeout(() => {
    cardElement.remove();
    renderDeck();
  }, 320);
}

function handleLike() {
  const topCard = document.querySelector(".top-card");
  const currentCafe = getCurrentSeedCafe();
  if (!topCard || !currentCafe) {
    return;
  }

  topCard.style.transition =
    "transform .35s cubic-bezier(.25,.8,.25,1), opacity .25s";
  doLike(topCard, currentCafe);
}

function handleNope() {
  const topCard = document.querySelector(".top-card");
  const currentCafe = getCurrentSeedCafe();

  if (topCard && currentCafe) {
    topCard.style.transition =
      "transform .35s cubic-bezier(.25,.8,.25,1), opacity .25s";
    doNope(topCard, currentCafe);
    return;
  }

  if (state.selectedSeedCafes.length > 0) {
    void startAnalysis();
  }
}

function handleLocation() {
  const currentCafe = getCurrentSeedCafe();
  if (!currentCafe) {
    return;
  }
  openExternalUrl(currentCafe.google_maps_url);
}

async function startAnalysis() {
  if (state.isAnalyzing || state.selectedSeedCafes.length === 0) {
    return;
  }

  state.isAnalyzing = true;
  disableSwipeButtons(true);
  showScreen("screen-loading");
  resetLoadingAnimation();

  let stepIndex = 0;
  state.loadingIntervalId = window.setInterval(() => {
    stepIndex += 1;
    if (stepIndex < LOADING_STEPS.length) {
      elements.loadingText.textContent = LOADING_STEPS[stepIndex];
    }
  }, 600);

  try {
    const [recommendation] = await Promise.all([
      api.recommend(
        state.selectedSeedCafes.map((cafe) => cafe.id),
        [...state.excludedResultCafeIds],
      ),
      wait(2200),
    ]);

    state.recommendation = recommendation;
    state.topResults = recommendation.results;

    if (recommendation.fallback_message) {
      toast(recommendation.fallback_message, "warn");
    }

    showResults();
  } catch (error) {
    toast(error.message, "warn");
    showScreen("screen-swipe");
  } finally {
    if (state.loadingIntervalId) {
      window.clearInterval(state.loadingIntervalId);
      state.loadingIntervalId = null;
    }
    state.isAnalyzing = false;
    disableSwipeButtons(false);
  }
}

function showResults() {
  showScreen("screen-results");

  elements.resultsTags.innerHTML = "";
  state.selectedSeedCafes.forEach((cafe) => {
    const tag = document.createElement("div");
    tag.className = "vibe-tag";
    tag.textContent = cafe.category;
    elements.resultsTags.appendChild(tag);
  });

  if (!state.recommendation || !state.recommendation.results.length) {
    elements.resultsDesc.textContent =
      state.recommendation?.fallback_message ||
      "We could not find matching cafes from the current dataset.";
    elements.resultsList.innerHTML = `
      <div class="result-card">
        <div class="result-card-body">
          <div class="result-reason">No cafe matches are available right now. Please try another seed selection.</div>
        </div>
      </div>
    `;
    return;
  }

  const selectedNames = state.recommendation.selected_seed_cafes
    .map((cafe) => cafe.name)
    .join(" + ");
  elements.resultsDesc.textContent = `Matched from ${selectedNames}`;

  elements.resultsList.innerHTML = "";
  state.topResults.forEach((result) => {
    elements.resultsList.appendChild(buildResultCard(result));
  });
}

function buildResultCard(cafe) {
  const card = document.createElement("div");
  card.className = "result-card";

  const matchPercentage = roundMatchPercentage(cafe.similarity_score);
  card.innerHTML = `
    <img class="result-card-img" loading="lazy">
    <div class="result-card-body">
      <div class="result-card-top">
        <div class="result-cafe-name"></div>
        <div class="match-badge"></div>
      </div>
      <div class="result-stars"><span class="star-icons"></span><span class="star-value"></span></div>
      <div class="result-address">
        <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#C4956A" stroke-width="2.2" stroke-linecap="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        <span class="address-value"></span>
      </div>
      <div class="result-reason"></div>
      <div class="result-action-row">
        <button class="btn-maps-small" type="button">
          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
          Google Maps
        </button>
        <button class="btn-detail-small" type="button">View Details →</button>
      </div>
    </div>
  `;

  card.querySelector(".result-card-img").src = cafe.image_url;
  card.querySelector(".result-card-img").alt = cafe.name;
  card.querySelector(".result-cafe-name").textContent = cafe.name;
  card.querySelector(".match-badge").textContent = `${matchPercentage}% match`;
  card.querySelector(".star-icons").innerHTML = renderStars(cafe.rating);
  card.querySelector(".star-value").textContent = cafe.rating;
  card.querySelector(".address-value").textContent = cafe.address;
  card.querySelector(".result-reason").textContent = cafe.reason;
  card
    .querySelector(".btn-maps-small")
    .addEventListener("click", () => openExternalUrl(cafe.google_maps_url));
  card
    .querySelector(".btn-detail-small")
    .addEventListener("click", () => openDetail(cafe.id));

  return card;
}

function openDetail(cafeId) {
  const cafe =
    state.topResults.find((result) => result.id === cafeId) || state.currentDetailCafe;
  if (!cafe) {
    return;
  }

  state.currentDetailCafe = cafe;
  const matchPercentage = roundMatchPercentage(cafe.similarity_score || 0);

  elements.detail.image.src = cafe.image_url;
  elements.detail.image.alt = cafe.name;
  elements.detail.match.textContent = `${matchPercentage}% Match`;
  elements.detail.name.textContent = cafe.name;
  elements.detail.cat.textContent = cafe.category;
  elements.detail.address.textContent = cafe.address;
  elements.detail.rating.textContent = `${cafe.rating} / 5.0`;
  elements.detail.category.textContent = cafe.category;
  elements.detail.reason.textContent = cafe.reason;
  elements.detail.mapsButton.onclick = () => openExternalUrl(cafe.google_maps_url);

  if (elements.detail.spectrum?.closest(".detail-section")) {
    elements.detail.spectrum.closest(".detail-section").style.display = "none";
  }
  if (elements.detail.busy?.closest(".detail-section")) {
    elements.detail.busy.closest(".detail-section").style.display = "none";
  }

  showScreen("screen-detail");
}

function toast(message, type = "info") {
  const toastElement = document.createElement("div");
  toastElement.className = `toast toast-${type}`;
  toastElement.innerHTML = `<span>${message}</span>`;
  elements.toasts.appendChild(toastElement);
  window.setTimeout(() => toastElement.remove(), 2600);
}

function initializeApp() {
  updateClock();
  window.setInterval(updateClock, 1000);
  updateSelectionCounter();

  if (elements.detail.spectrum?.closest(".detail-section")) {
    elements.detail.spectrum.closest(".detail-section").style.display = "none";
  }
  if (elements.detail.busy?.closest(".detail-section")) {
    elements.detail.busy.closest(".detail-section").style.display = "none";
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

document.addEventListener("DOMContentLoaded", initializeApp);
