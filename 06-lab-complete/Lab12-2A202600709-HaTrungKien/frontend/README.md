# Frontend Contract

Frontend du kien la web app nhe bang `HTML + Tailwind CDN + Lucide + Vanilla JS`.

## Contract voi backend

- Backend tra `GET /api/seed-cafes` de hien 5 anh seed cho user chon.
- Moi seed cafe den truc tiep tu database, khong con `vibe` co dinh trong repo.
- Frontend gui `POST /api/recommend` voi `selected_seed_cafe_ids`.
- Frontend gui `POST /api/feedback` voi `selected_seed_cafe_ids` va `cafe_id`.

Neu user khong thich ca 5 seed hien tai:

- frontend goi lai `GET /api/seed-cafes`
- kem `excluded_seed_cafe_ids`
- backend random 5 seed khac tu category khac neu con

## Frontend files

- `index.html` giu layout va style chinh
- `frontend/js/app.js` chua toan bo state, rendering, va API integration

## API base URL

- Mac dinh frontend se goi `http://127.0.0.1:8000` khi chay local
- Co the override bang `window.COFFEEHOLIC_CONFIG = { apiBaseUrl: "..." }`
- Hoac set `data-api-base-url` tren the `body`
