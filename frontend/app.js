const API_BASE = "/api";
const tg = window.Telegram?.WebApp;

if (tg) {
  tg.ready();
  tg.expand();
}

const iconMap = {
  wallpaper: "🧱",
  tools: "🧰",
  ac_unit: "❄️",
  default: "🛠️",
};

const scrollButtons = document.querySelectorAll("[data-scroll]");
scrollButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = document.getElementById(btn.dataset.scroll);
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

const servicesGrid = document.getElementById("services-grid");
const portfolioGrid = document.getElementById("portfolio-grid");

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("API error");
  return res.json();
}

function renderServices(services) {
  servicesGrid.innerHTML = "";
  services.forEach((service) => {
    const card = document.createElement("article");
    card.className = "card";
    const icon = iconMap[service.icon] || iconMap.default;
    card.innerHTML = `
      <span class="service-icon">${icon}</span>
      <h3>${service.name}</h3>
      <p>${service.description}</p>
      <strong>${service.price}</strong>
    `;
    servicesGrid.appendChild(card);
  });
}

function renderPortfolio(items) {
  portfolioGrid.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `
      <img src="${item.image_url}" alt="${item.title}" data-id="${item.id}" />
      <h3>${item.title}</h3>
      <p>${item.description}</p>
      <div class="badges">
        <span class="badge">${item.wallpaper_type}</span>
        <span class="badge">${item.area_sqm} м²</span>
      </div>
    `;
    card.querySelector("img").addEventListener("click", () => openLightbox(item));
    portfolioGrid.appendChild(card);
  });
}

async function bootstrapContent() {
  try {
    const [services, portfolio] = await Promise.all([
      fetchJSON(`${API_BASE}/services/`),
      fetchJSON(`${API_BASE}/portfolio/`),
    ]);
    renderServices(services);
    renderPortfolio(portfolio);
  } catch (error) {
    console.error("Failed to load content", error);
  }
}

const lightbox = document.getElementById("lightbox");
const lightboxImage = document.getElementById("lightbox-image");
const lightboxTitle = document.getElementById("lightbox-title");
const lightboxDescription = document.getElementById("lightbox-description");
const lightboxClose = document.getElementById("lightbox-close");

function openLightbox(item) {
  lightboxImage.src = item.image_url;
  lightboxImage.alt = item.title;
  lightboxTitle.textContent = item.title;
  lightboxDescription.textContent = `${item.wallpaper_type} • ${item.area_sqm} м² • ${item.highlights}`;
  lightbox.classList.add("open");
  lightbox.setAttribute("aria-hidden", "false");
}

function closeLightbox() {
  lightbox.classList.remove("open");
  lightbox.setAttribute("aria-hidden", "true");
}

lightbox.addEventListener("click", (event) => {
  if (event.target === lightbox) closeLightbox();
});
lightboxClose.addEventListener("click", closeLightbox);

const btnEstimate = document.getElementById("btn-estimate");
const btnWrite = document.getElementById("btn-write");
const tgHandle = document.getElementById("tg-handle");

function openChat() {
  const url = tgHandle.href;
  if (tg?.openTelegramLink) {
    tg.openTelegramLink(url);
  } else {
    window.open(url, "_blank");
  }
}

btnWrite.addEventListener("click", openChat);

document.getElementById("year").textContent = new Date().getFullYear();

btnEstimate.addEventListener("click", async () => {
  if (!tg?.initData) {
    alert("Откройте мини-приложение внутри Telegram, чтобы отправить запрос.");
    return;
  }

  btnEstimate.disabled = true;
  btnEstimate.textContent = "Отправляем...";

  try {
    const response = await fetch(`${API_BASE}/requests/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        details: "Запрос из mini app",
        init_data: tg.initData,
      }),
    });

    if (!response.ok) throw new Error("Не удалось отправить запрос");
    if (tg?.showPopup) {
      tg.showPopup({ title: "Отлично", message: "Я свяжусь с вами в ближайшее время." });
    } else {
      alert("Запрос принят! Я свяжусь с вами.");
    }
  } catch (error) {
    console.error(error);
    if (tg?.showPopup) {
      tg.showPopup({ title: "Ошибка", message: "Попробуйте повторить чуть позже." });
    } else {
      alert("Ошибка: не удалось отправить запрос");
    }
  } finally {
    btnEstimate.disabled = false;
    btnEstimate.textContent = "Получить расчет стоимости";
  }
});

bootstrapContent();
